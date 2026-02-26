from __future__ import annotations

import json
from importlib import import_module
from typing import Any

from .kafka_config import KafkaSettings


class KafkaControlProducer:
    def __init__(self, *, settings: KafkaSettings) -> None:
        kafka = import_module("kafka")
        self._settings = settings
        self._producer = kafka.KafkaProducer(bootstrap_servers=settings.brokers.split(","))

    def send_control_action(self, action: dict[str, Any]) -> None:
        payload = json.dumps(action, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self._producer.send(self._settings.control_topic, value=payload)


class KafkaTelemetryProducer:
    def __init__(self, *, settings: KafkaSettings) -> None:
        kafka = import_module("kafka")
        self._settings = settings
        self._producer = kafka.KafkaProducer(bootstrap_servers=settings.brokers.split(","))

    def send_telemetry(self, message: dict[str, Any]) -> None:
        stream_id = str(message.get("stream_id") or "").strip()
        if not stream_id:
            raise ValueError("stream_id is required for partition key routing")
        payload = json.dumps(message, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self._producer.send(self._settings.telemetry_topic, key=stream_id.encode("utf-8"), value=payload)
