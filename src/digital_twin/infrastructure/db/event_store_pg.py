from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum
from time import perf_counter
from typing import Any
from uuid import UUID

import psycopg

from digital_twin.application.ports.event_store import EventStore
from digital_twin.domain.event import DomainEvent

from .metrics import DBAdapterMetrics
from .postgres import canonical_payload_sha256, connection_scope


class AppendResult(str, Enum):
    APPENDED = "APPENDED"
    ALREADY_EXISTS = "ALREADY_EXISTS"


class VersionConflictError(ValueError):
    pass


class BatchAppendError(ValueError):
    pass


@dataclass(frozen=True)
class AppendRequest:
    event: DomainEvent
    stream_id: str
    version_counter: int
    event_type: str
    payload: dict[str, Any]
    ingest_id: UUID


class EventStorePG(EventStore):
    """Policy: append_batch is atomic and fail-fast on any ALREADY_EXISTS member."""

    def __init__(self, *, dsn: str | None = None, stream_id: str = "default", metrics: DBAdapterMetrics | None = None) -> None:
        self._dsn = dsn
        self._stream_id = stream_id
        self._metrics = metrics or DBAdapterMetrics()

    @property
    def metrics(self) -> DBAdapterMetrics:
        return self._metrics

    def _build_request(
        self,
        event: DomainEvent,
        *,
        stream_id: str | None,
        version_counter: int | None,
        event_type: str | None,
        payload: dict[str, Any] | None,
        ingest_id: UUID | None,
    ) -> AppendRequest:
        row_stream_id = stream_id or self._stream_id
        row_version = int(version_counter if version_counter is not None else event.version)
        row_event_type = event_type or event.type
        row_payload = payload if payload is not None else dict(event.payload)
        row_ingest_id = ingest_id or event.event_id
        return AppendRequest(
            event=event,
            stream_id=row_stream_id,
            version_counter=row_version,
            event_type=row_event_type,
            payload=row_payload,
            ingest_id=row_ingest_id,
        )

    def append(
        self,
        event: DomainEvent,
        *,
        stream_id: str | None = None,
        version_counter: int | None = None,
        event_type: str | None = None,
        payload: dict[str, Any] | None = None,
        ingest_id: UUID | None = None,
    ) -> AppendResult:
        request = self._build_request(
            event,
            stream_id=stream_id,
            version_counter=version_counter,
            event_type=event_type,
            payload=payload,
            ingest_id=ingest_id,
        )

        started = perf_counter()
        try:
            with connection_scope(dsn=self._dsn) as conn:
                result = self._append_within_transaction(conn, request)
                conn.commit()
            self._metrics.record_event_append_latency((perf_counter() - started) * 1000.0)
            return result
        except Exception:
            self._metrics.record_event_append_error()
            self._metrics.record_query_error()
            raise

    def append_batch(self, batch: Sequence[AppendRequest]) -> tuple[AppendResult, ...]:
        """Atomic batch append in caller-provided deterministic order."""

        started = perf_counter()
        results: list[AppendResult] = []
        try:
            with connection_scope(dsn=self._dsn) as conn:
                for req in batch:
                    result = self._append_within_transaction(conn, req)
                    if result is AppendResult.ALREADY_EXISTS:
                        raise BatchAppendError(
                            f"append_batch encountered ALREADY_EXISTS for stream_id={req.stream_id} ingest_id={req.ingest_id}"
                        )
                    results.append(result)
                conn.commit()
            self._metrics.record_event_append_latency((perf_counter() - started) * 1000.0)
            return tuple(results)
        except Exception:
            self._metrics.record_event_append_error()
            self._metrics.record_query_error()
            raise

    def _append_within_transaction(self, conn: psycopg.Connection[Any], request: AppendRequest) -> AppendResult:
        payload_hash = canonical_payload_sha256(request.payload)

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO event_log (
                        stream_id,
                        version_counter,
                        event_type,
                        payload,
                        payload_sha256,
                        ingest_id
                    ) VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                    ON CONFLICT (stream_id, ingest_id)
                    DO NOTHING
                    RETURNING seq
                    """,
                    (
                        request.stream_id,
                        request.version_counter,
                        request.event_type,
                        json.dumps(request.payload, sort_keys=True, separators=(",", ":")),
                        payload_hash,
                        request.ingest_id,
                    ),
                )
                inserted = cur.fetchone()
                if inserted is not None:
                    return AppendResult.APPENDED

                cur.execute(
                    """
                    SELECT version_counter, event_type, payload, payload_sha256
                    FROM event_log
                    WHERE stream_id = %s AND ingest_id = %s
                    """,
                    (request.stream_id, request.ingest_id),
                )
                existing = cur.fetchone()
                if existing is None:
                    raise RuntimeError("idempotency conflict lookup returned no row")

                existing_version, existing_type, existing_payload, existing_hash = existing
                if (
                    int(existing_version) != request.version_counter
                    or str(existing_type) != request.event_type
                    or dict(existing_payload) != request.payload
                    or bytes(existing_hash) != payload_hash
                ):
                    raise BatchAppendError(
                        "ingest_id collision with different payload/version detected "
                        f"for stream_id={request.stream_id} ingest_id={request.ingest_id}"
                    )
                return AppendResult.ALREADY_EXISTS
        except psycopg.errors.UniqueViolation as exc:
            constraint = getattr(exc.diag, "constraint_name", "")
            if "version" in (constraint or ""):
                raise VersionConflictError(
                    f"Version conflict for stream_id={request.stream_id} version_counter={request.version_counter}"
                ) from exc
            raise

    def load_all(self, stream_id: str | None = None) -> Iterable[DomainEvent]:
        row_stream_id = stream_id or self._stream_id
        try:
            with connection_scope(dsn=self._dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT version_counter, event_type, payload
                        FROM event_log
                        WHERE stream_id = %s
                        ORDER BY seq ASC
                        """,
                        (row_stream_id,),
                    )
                    rows = cur.fetchall()
        except Exception:
            self._metrics.record_query_error()
            raise

        return tuple(
            DomainEvent(timestamp=int(version_counter), type=event_type, payload=payload, version=int(version_counter))
            for version_counter, event_type, payload in rows
        )

    def load_from(self, version: int, stream_id: str | None = None) -> Iterable[DomainEvent]:
        row_stream_id = stream_id or self._stream_id
        try:
            with connection_scope(dsn=self._dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT version_counter, event_type, payload
                        FROM event_log
                        WHERE stream_id = %s AND version_counter > %s
                        ORDER BY seq ASC
                        """,
                        (row_stream_id, version),
                    )
                    rows = cur.fetchall()
        except Exception:
            self._metrics.record_query_error()
            raise

        return tuple(
            DomainEvent(timestamp=int(version_counter), type=event_type, payload=payload, version=int(version_counter))
            for version_counter, event_type, payload in rows
        )
