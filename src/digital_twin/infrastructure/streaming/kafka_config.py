from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KafkaSettings:
    brokers: str = "localhost:9092"
    telemetry_topic: str = "dt.telemetry"
    dlq_topic: str = "dt.telemetry.dlq"
    control_topic: str = "dt.control"
    group_id: str = "digital-twin-ingest"
    client_id: str | None = None
    max_poll_records: int = 100
    stream_id: str = "dc1"

    @classmethod
    def from_env(cls) -> "KafkaSettings":
        max_poll_records = int(os.getenv("KAFKA_MAX_POLL_RECORDS", str(cls.max_poll_records)))
        group_id = os.getenv("KAFKA_CONSUMER_GROUP", cls.group_id).strip()
        if not group_id:
            raise ValueError("KAFKA_CONSUMER_GROUP/group_id is required")
        client_id = os.getenv("KAFKA_CLIENT_ID")
        return cls(
            brokers=os.getenv("KAFKA_BROKERS", cls.brokers),
            telemetry_topic=os.getenv("KAFKA_TOPIC_TELEMETRY", cls.telemetry_topic),
            dlq_topic=os.getenv("KAFKA_TOPIC_DLQ", cls.dlq_topic),
            control_topic=os.getenv("KAFKA_TOPIC_CONTROL", cls.control_topic),
            group_id=group_id,
            client_id=client_id.strip() if client_id else None,
            max_poll_records=max_poll_records,
            stream_id=os.getenv("STREAM_ID", cls.stream_id),
        )
