from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import monotonic
from types import SimpleNamespace
from typing import Any, Callable

from digital_twin.domain.twin import DataCenterTwin

from .message_schema import KafkaValidationError
from .normalizer import normalize_kafka_message
from .streaming_metrics import StreamingMetricsCollector


class IngestionStatus(str, Enum):
    APPLIED = "APPLIED"
    DUPLICATE = "DUPLICATE"
    DLQ = "DLQ"
    VERSION_CONFLICT = "VERSION_CONFLICT"


@dataclass(frozen=True, slots=True)
class IngestionOutcome:
    stream_id: str
    ingest_id: str
    status: IngestionStatus
    kafka_context: dict[str, Any]
    dlq_reason: str | None = None
    raw_message: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class CoordinatorSettings:
    max_active_streams: int = 512
    stream_ttl_seconds: int = 1800
    eviction_policy: str = "LRU"
    eviction_batch_size: int = 32

    def __post_init__(self) -> None:
        if self.max_active_streams <= 0:
            raise ValueError("max_active_streams must be > 0")
        if self.stream_ttl_seconds <= 0:
            raise ValueError("stream_ttl_seconds must be > 0")
        if self.eviction_policy != "LRU":
            raise ValueError("eviction_policy must be 'LRU'")
        if self.eviction_batch_size <= 0:
            raise ValueError("eviction_batch_size must be > 0")


@dataclass(slots=True)
class StreamEntry:
    twin: DataCenterTwin
    last_seen_monotonic: float
    created_monotonic: float


@dataclass(frozen=True, slots=True)
class EvictionOutcome:
    stream_id: str
    evicted: bool
    reason: str


class MultiStreamCoordinator:
    """Routes each stream to an isolated DataCenterTwin instance with TTL/LRU eviction."""

    def __init__(
        self,
        *,
        twin_factory: Callable[[str], DataCenterTwin] | None = None,
        default_stream_id: str = "dc1",
        settings: CoordinatorSettings | None = None,
        metrics: StreamingMetricsCollector | None = None,
        monotonic_clock: Callable[[], float] = monotonic,
    ) -> None:
        self._twin_factory = twin_factory or default_twin_factory
        self._default_stream_id = default_stream_id
        self._settings = settings or CoordinatorSettings()
        self._metrics = metrics or StreamingMetricsCollector()
        self._clock = monotonic_clock
        self._streams: dict[str, StreamEntry] = {}
        self._handled_count = 0
        self._metrics.set_streams_active_gauge(0)

    @property
    def metrics(self) -> StreamingMetricsCollector:
        return self._metrics

    @property
    def twins(self) -> dict[str, DataCenterTwin]:
        return {stream_id: entry.twin for stream_id, entry in self._streams.items()}

    def active_stream_count(self) -> int:
        return len(self._streams)

    def handle_message(self, message: dict[str, Any], *, kafka_context: dict[str, Any]) -> IngestionOutcome:
        started = self._clock()
        now = started
        try:
            event, parsed = normalize_kafka_message(
                message,
                default_stream_id=self._default_stream_id,
                context=SimpleNamespace(
                    partition=int(kafka_context.get("partition", -1)),
                    offset=int(kafka_context.get("offset", -1)),
                ),
            )
            stream_id = parsed.stream_id
            twin = self._resolve_twin(stream_id, now)
            twin.ingest_event(event)
            append_result = getattr(twin, "last_append_result", None)
            status = IngestionStatus.DUPLICATE if getattr(append_result, "value", append_result) == "ALREADY_EXISTS" else IngestionStatus.APPLIED
            outcome = IngestionOutcome(
                stream_id=stream_id,
                ingest_id=str(parsed.ingest_id),
                status=status,
                kafka_context=dict(kafka_context),
            )
        except Exception as exc:
            if exc.__class__.__name__ == "VersionConflictError":
                stream_id = str(message.get("stream_id") or self._default_stream_id)
                outcome = IngestionOutcome(
                    stream_id=stream_id,
                    ingest_id=str(message.get("ingest_id") or ""),
                    status=IngestionStatus.VERSION_CONFLICT,
                    kafka_context=dict(kafka_context),
                    dlq_reason=str(exc),
                    raw_message=dict(message),
                )
            elif isinstance(exc, (KafkaValidationError, ValueError)):
                stream_id = str(message.get("stream_id") or self._default_stream_id)
                outcome = IngestionOutcome(
                    stream_id=stream_id,
                    ingest_id=str(message.get("ingest_id") or ""),
                    status=IngestionStatus.DLQ,
                    kafka_context=dict(kafka_context),
                    dlq_reason=str(exc),
                    raw_message=dict(message),
                )
            else:
                raise

        if outcome.stream_id in self._streams:
            self._streams[outcome.stream_id].last_seen_monotonic = now

        self._handled_count += 1
        self._metrics.record_outcome(status=outcome.status.value)
        self._metrics.record_handle_latency_ms((self._clock() - started) * 1000.0)

        if self._handled_count % self._settings.eviction_batch_size == 0:
            self.maybe_evict(now_monotonic=now)

        if self.active_stream_count() > self._settings.max_active_streams:
            self._evict_for_capacity(now)

        self._metrics.set_streams_active_gauge(self.active_stream_count())
        return outcome


    def ingest_event(self, *, stream_id: str, event: Any, ingest_id: str) -> IngestionOutcome:
        """Apply a pre-normalized event through the canonical per-stream ingestion path."""

        started = self._clock()
        now = started
        try:
            twin = self._resolve_twin(stream_id, now)
            twin.ingest_event(event)
            append_result = getattr(twin, "last_append_result", None)
            status = IngestionStatus.DUPLICATE if getattr(append_result, "value", append_result) == "ALREADY_EXISTS" else IngestionStatus.APPLIED
            outcome = IngestionOutcome(
                stream_id=stream_id,
                ingest_id=ingest_id,
                status=status,
                kafka_context={},
            )
        except Exception as exc:
            if exc.__class__.__name__ == "VersionConflictError":
                outcome = IngestionOutcome(
                    stream_id=stream_id,
                    ingest_id=ingest_id,
                    status=IngestionStatus.VERSION_CONFLICT,
                    kafka_context={},
                    dlq_reason=str(exc),
                    raw_message=None,
                )
            elif isinstance(exc, (KafkaValidationError, ValueError)):
                outcome = IngestionOutcome(
                    stream_id=stream_id,
                    ingest_id=ingest_id,
                    status=IngestionStatus.DLQ,
                    kafka_context={},
                    dlq_reason=str(exc),
                    raw_message=None,
                )
            else:
                raise

        if outcome.stream_id in self._streams:
            self._streams[outcome.stream_id].last_seen_monotonic = now

        self._handled_count += 1
        self._metrics.record_outcome(status=outcome.status.value)
        self._metrics.record_handle_latency_ms((self._clock() - started) * 1000.0)

        if self._handled_count % self._settings.eviction_batch_size == 0:
            self.maybe_evict(now_monotonic=now)

        if self.active_stream_count() > self._settings.max_active_streams:
            self._evict_for_capacity(now)

        self._metrics.set_streams_active_gauge(self.active_stream_count())
        return outcome

    def maybe_evict(self, *, now_monotonic: float | None = None) -> tuple[EvictionOutcome, ...]:
        now = self._clock() if now_monotonic is None else now_monotonic
        candidates = self.evict_candidates(now)
        outcomes = [self.evict(stream_id, reason="TTL") for stream_id in candidates]
        self._metrics.set_streams_active_gauge(self.active_stream_count())
        return tuple(outcomes)

    def evict_candidates(self, now_monotonic: float) -> list[str]:
        ttl = float(self._settings.stream_ttl_seconds)
        stale = [
            (stream_id, entry.last_seen_monotonic)
            for stream_id, entry in self._streams.items()
            if now_monotonic - entry.last_seen_monotonic >= ttl
        ]
        stale.sort(key=lambda item: item[1])
        return [stream_id for stream_id, _ in stale]

    def evict(self, stream_id: str, *, reason: str) -> EvictionOutcome:
        entry = self._streams.get(stream_id)
        if entry is None:
            return EvictionOutcome(stream_id=stream_id, evicted=False, reason=reason)
        self._safe_flush(entry.twin)
        del self._streams[stream_id]
        self._metrics.record_eviction(reason=reason)
        self._metrics.set_streams_active_gauge(self.active_stream_count())
        return EvictionOutcome(stream_id=stream_id, evicted=True, reason=reason)

    def _resolve_twin(self, stream_id: str, now: float) -> DataCenterTwin:
        entry = self._streams.get(stream_id)
        if entry is None:
            twin = self._twin_factory(stream_id)
            entry = StreamEntry(twin=twin, last_seen_monotonic=now, created_monotonic=now)
            self._streams[stream_id] = entry
        return entry.twin

    def _evict_for_capacity(self, now: float) -> None:
        _ = now
        to_remove = self.active_stream_count() - self._settings.max_active_streams
        if to_remove <= 0:
            return
        lru = sorted(self._streams.items(), key=lambda item: item[1].last_seen_monotonic)
        for stream_id, _entry in lru[:to_remove]:
            self.evict(stream_id, reason="CAPACITY")

    @staticmethod
    def _safe_flush(twin: DataCenterTwin) -> None:
        for hook_name in ("flush", "flush_state", "close"):
            hook = getattr(twin, hook_name, None)
            if callable(hook):
                hook()
                return


def default_twin_factory(stream_id: str) -> DataCenterTwin:
    from digital_twin.infrastructure.db.event_store_pg import EventStorePG
    from digital_twin.infrastructure.db.snapshot_store_pg import SnapshotStorePG

    return DataCenterTwin(
        event_store=EventStorePG(stream_id=stream_id),
        snapshot_store=SnapshotStorePG(stream_id=stream_id),
        persistence_stream_id=stream_id,
    )
