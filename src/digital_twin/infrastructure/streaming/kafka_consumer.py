from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from .coordinator import IngestionStatus, MultiStreamCoordinator
from .kafka_config import KafkaSettings
from .message_schema import KafkaValidationError


@dataclass(frozen=True, slots=True)
class KafkaMessageContext:
    topic: str
    partition: int
    offset: int


class _RebalanceListener:
    def __init__(self, adapter: "KafkaConsumerAdapter") -> None:
        self._adapter = adapter

    def on_partitions_revoked(self, revoked: list[Any]) -> None:
        self._adapter.on_partitions_revoked(revoked)

    def on_partitions_assigned(self, assigned: list[Any]) -> None:
        self._adapter.on_partitions_assigned(assigned)


class KafkaConsumerAdapter:
    def __init__(
        self,
        *,
        settings: KafkaSettings,
        coordinator: MultiStreamCoordinator,
        consumer: Any | None = None,
        producer: Any | None = None,
    ) -> None:
        self._settings = settings
        self._coordinator = coordinator
        self._consumer = consumer or self._build_consumer(settings)
        self._producer = producer or self._build_producer(settings)
        self._revoked_partitions: set[tuple[str, int]] = set()
        self._assigned_partitions: set[tuple[str, int]] = set()

        try:
            self._consumer.subscribe([settings.telemetry_topic], listener=_RebalanceListener(self))
        except TypeError:
            self._consumer.subscribe([settings.telemetry_topic])

    def poll_forever(self) -> None:
        for message in self._consumer:
            self._refresh_assignment_state()
            self._handle_message(message)

    def poll_once(self, timeout_ms: int = 1000) -> bool:
        message_pack = self._consumer.poll(timeout_ms=timeout_ms)
        self._refresh_assignment_state()
        for _tp, records in message_pack.items():
            for message in records:
                self._handle_message(message)
                return True
        return False

    def on_partitions_revoked(self, revoked: list[Any]) -> None:
        self._revoked_partitions = {(str(tp.topic), int(tp.partition)) for tp in revoked}
        try:
            self._consumer.commit()
        except Exception:
            return

    def on_partitions_assigned(self, assigned: list[Any]) -> None:
        self._assigned_partitions = {(str(tp.topic), int(tp.partition)) for tp in assigned}
        self._revoked_partitions.clear()

    def _refresh_assignment_state(self) -> None:
        assignment_getter = getattr(self._consumer, "assignment", None)
        if not callable(assignment_getter):
            return
        try:
            assignment = assignment_getter()
        except Exception:
            return
        assigned = {(str(tp.topic), int(tp.partition)) for tp in assignment}
        self._assigned_partitions = assigned

    def _is_processing_allowed(self, context: KafkaMessageContext) -> bool:
        key = (context.topic, context.partition)
        if key in self._revoked_partitions:
            return False
        if self._assigned_partitions and key not in self._assigned_partitions:
            return False
        return True

    def _handle_message(self, message: Any) -> None:
        context = KafkaMessageContext(
            topic=str(getattr(message, "topic", self._settings.telemetry_topic)),
            partition=int(message.partition),
            offset=int(message.offset),
        )
        if not self._is_processing_allowed(context):
            return

        raw_message: dict[str, Any]
        try:
            raw_message = self._deserialize_message(message.value)
        except KafkaValidationError as exc:
            self._publish_dlq(raw_message={}, reason=str(exc), context=context)
            self._commit()
            return

        outcome = self._coordinator.handle_message(
            raw_message,
            kafka_context={"topic": context.topic, "partition": context.partition, "offset": context.offset},
        )

        self._record_lag_hint(message)

        if outcome.status is IngestionStatus.VERSION_CONFLICT:
            raise RuntimeError(
                f"Version conflict for stream_id={outcome.stream_id} at topic={context.topic} partition={context.partition} offset={context.offset}"
            )

        if outcome.status is IngestionStatus.DLQ:
            self._publish_dlq(
                raw_message=outcome.raw_message or raw_message,
                reason=outcome.dlq_reason or "validation/transition failure",
                context=context,
            )
            self._commit()
            return

        if outcome.status in (IngestionStatus.APPLIED, IngestionStatus.DUPLICATE):
            self._commit()
            return

        raise RuntimeError(f"Unsupported ingestion outcome status={outcome.status}")

    def _record_lag_hint(self, message: Any) -> None:
        metrics = getattr(self._coordinator, "metrics", None)
        if metrics is None:
            return
        lag = getattr(message, "highwater", None)
        if lag is None:
            metrics.set_kafka_lag_last(None)
            return
        try:
            offset = int(message.offset)
            highwater = int(lag() if callable(lag) else lag)
            metrics.set_kafka_lag_last(max(0, highwater - offset - 1))
        except Exception:
            metrics.set_kafka_lag_last(None)

    def _publish_dlq(self, *, raw_message: dict[str, Any], reason: str, context: KafkaMessageContext) -> None:
        dlq_payload = {
            "error": reason,
            "raw_message": raw_message,
            "kafka_topic": context.topic,
            "kafka_partition": context.partition,
            "kafka_offset": context.offset,
        }
        encoded = json.dumps(dlq_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self._producer.send(self._settings.dlq_topic, value=encoded)

    def _commit(self) -> None:
        self._consumer.commit()

    @staticmethod
    def _deserialize_message(payload: bytes | str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        loaded = json.loads(text)
        if not isinstance(loaded, dict):
            raise KafkaValidationError("Kafka message must decode to a JSON object")
        return loaded

    @staticmethod
    def _build_consumer(settings: KafkaSettings) -> Any:
        kafka = import_module("kafka")
        kwargs: dict[str, Any] = {
            "bootstrap_servers": settings.brokers.split(","),
            "group_id": settings.group_id,
            "enable_auto_commit": False,
            "auto_offset_reset": "earliest",
            "max_poll_records": settings.max_poll_records,
            "consumer_timeout_ms": 1000,
        }
        if settings.client_id:
            kwargs["client_id"] = settings.client_id
        return kafka.KafkaConsumer(**kwargs)

    @staticmethod
    def _build_producer(settings: KafkaSettings) -> Any:
        kafka = import_module("kafka")
        return kafka.KafkaProducer(bootstrap_servers=settings.brokers.split(","))
