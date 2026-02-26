from __future__ import annotations

import json
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from time import perf_counter
from typing import Any

from digital_twin.infrastructure.ingestion.message_contract import TelemetryValidationError
from digital_twin.infrastructure.ingestion.normalize import normalize_message_to_domain_event
from digital_twin.infrastructure.streaming.coordinator import IngestionStatus, MultiStreamCoordinator


@dataclass(slots=True)
class HTTPIngestionMetrics:
    """Side-channel metrics for HTTP ingestion requests."""

    ingestion_latency_ms: list[float] = field(default_factory=list)
    status_counts: dict[str, int] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def record(self, *, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self.ingestion_latency_ms.append(latency_ms)
            key = str(status_code)
            self.status_counts[key] = self.status_counts.get(key, 0) + 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            latencies = tuple(self.ingestion_latency_ms)
            return {
                "request_count": len(latencies),
                "status_counts": dict(self.status_counts),
                "latency_ms": {
                    "avg": (sum(latencies) / len(latencies)) if latencies else 0.0,
                    "max": max(latencies) if latencies else 0.0,
                },
            }


class IngestionAPIHandler(BaseHTTPRequestHandler):
    coordinator: MultiStreamCoordinator
    default_stream_id: str
    require_ingest_id: bool
    max_batch_size: int
    metrics: HTTPIngestionMetrics

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return
        if self.path == "/health/metrics":
            self._send_json(HTTPStatus.OK, self.metrics.snapshot())
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        started = perf_counter()
        if self.path == "/ingest":
            response_status, payload = self._handle_single()
            self.metrics.record(status_code=response_status.value, latency_ms=(perf_counter() - started) * 1000.0)
            self._send_json(response_status, payload)
            return
        if self.path == "/ingest/batch":
            response_status, payload = self._handle_batch()
            self.metrics.record(status_code=response_status.value, latency_ms=(perf_counter() - started) * 1000.0)
            self._send_json(response_status, payload)
            return
        self.metrics.record(status_code=HTTPStatus.NOT_FOUND.value, latency_ms=(perf_counter() - started) * 1000.0)
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def _handle_single(self) -> tuple[HTTPStatus, dict[str, Any]]:
        body, status, error_payload = self._parse_json_body()
        if body is None:
            return status, error_payload
        if not isinstance(body, dict):
            return HTTPStatus.BAD_REQUEST, {"dlq_reason": "body must be a JSON object", "error": "invalid_body"}
        return self._ingest_message(body)

    def _handle_batch(self) -> tuple[HTTPStatus, dict[str, Any]]:
        body, status, error_payload = self._parse_json_body()
        if body is None:
            return status, error_payload
        if not isinstance(body, list):
            return HTTPStatus.BAD_REQUEST, {"dlq_reason": "body must be a JSON array", "error": "invalid_body"}
        if len(body) > self.max_batch_size:
            return HTTPStatus.BAD_REQUEST, {
                "dlq_reason": f"batch size {len(body)} exceeds max_batch_size={self.max_batch_size}",
                "error": "batch_too_large",
            }

        ordered = sorted(body, key=lambda item: (str(item.get("source_time_utc", "")), str(item.get("ingest_id", ""))))
        items: list[dict[str, Any]] = []
        has_conflict = False
        has_bad_request = False
        for raw_item in ordered:
            if not isinstance(raw_item, dict):
                has_bad_request = True
                items.append({"error": "invalid_item", "dlq_reason": "batch item must be a JSON object", "status": "DLQ"})
                continue
            item_status, item_payload = self._ingest_message(raw_item)
            if item_status == HTTPStatus.CONFLICT:
                has_conflict = True
            elif item_status == HTTPStatus.BAD_REQUEST:
                has_bad_request = True
            items.append(item_payload)

        response_status = HTTPStatus.OK
        if has_conflict:
            response_status = HTTPStatus.CONFLICT
        elif has_bad_request:
            response_status = HTTPStatus.BAD_REQUEST

        return response_status, {
            "batch_ordering": "sorted(source_time_utc, ingest_id)",
            "count": len(items),
            "items": items,
        }

    def _ingest_message(self, message: dict[str, Any]) -> tuple[HTTPStatus, dict[str, Any]]:
        started = perf_counter()
        try:
            event, parsed = normalize_message_to_domain_event(
                message,
                default_stream_id=self.default_stream_id,
                require_ingest_id=self.require_ingest_id,
                observation_metadata={
                    "stream_id": str(message.get("stream_id") or self.default_stream_id),
                    "source": str(message.get("source") or ""),
                    "source_time_utc": str(message.get("source_time_utc") or ""),
                    "http_path": self.path,
                },
            )
            outcome = self.coordinator.ingest_event(
                stream_id=parsed.stream_id,
                event=event,
                ingest_id=str(parsed.ingest_id),
            )
            status_code = HTTPStatus.CONFLICT if outcome.status is IngestionStatus.VERSION_CONFLICT else HTTPStatus.OK
            payload = {
                "dlq_reason": outcome.dlq_reason,
                "ingest_id": str(parsed.ingest_id),
                "latency_ms": (perf_counter() - started) * 1000.0,
                "status": outcome.status.value,
                "stream_id": parsed.stream_id,
            }
            return status_code, payload
        except Exception as exc:
            if exc.__class__.__name__ == "VersionConflictError":
                return HTTPStatus.CONFLICT, {
                    "dlq_reason": str(exc),
                    "error": "version_conflict",
                    "ingest_id": str(message.get("ingest_id") or ""),
                    "status": IngestionStatus.VERSION_CONFLICT.value,
                    "stream_id": str(message.get("stream_id") or self.default_stream_id),
                }
            if isinstance(exc, (TelemetryValidationError, ValueError)):
                return HTTPStatus.BAD_REQUEST, {
                    "dlq_reason": str(exc),
                    "error": "validation_error",
                    "ingest_id": str(message.get("ingest_id") or ""),
                    "status": IngestionStatus.DLQ.value,
                    "stream_id": str(message.get("stream_id") or self.default_stream_id),
                }
            raise

    def _parse_json_body(self) -> tuple[dict[str, Any] | list[Any] | None, HTTPStatus, dict[str, Any]]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            return None, HTTPStatus.BAD_REQUEST, {"error": "invalid_json", "dlq_reason": "request body must be valid JSON"}
        return body, HTTPStatus.OK, {}

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class IngestionAPIServer(ThreadingHTTPServer):
    """HTTP server for deterministic ingestion gateway endpoints."""

    def __init__(
        self,
        server_address: tuple[str, int],
        *,
        coordinator: MultiStreamCoordinator,
        default_stream_id: str = "dc1",
        require_ingest_id: bool = True,
        max_batch_size: int = 128,
        metrics: HTTPIngestionMetrics | None = None,
    ) -> None:
        handler = _build_handler(
            coordinator=coordinator,
            default_stream_id=default_stream_id,
            require_ingest_id=require_ingest_id,
            max_batch_size=max_batch_size,
            metrics=metrics or HTTPIngestionMetrics(),
        )
        super().__init__(server_address, handler)


def _build_handler(
    *,
    coordinator: MultiStreamCoordinator,
    default_stream_id: str,
    require_ingest_id: bool,
    max_batch_size: int,
    metrics: HTTPIngestionMetrics,
) -> type[IngestionAPIHandler]:
    class _Handler(IngestionAPIHandler):
        pass

    _Handler.coordinator = coordinator
    _Handler.default_stream_id = default_stream_id
    _Handler.require_ingest_id = require_ingest_id
    _Handler.max_batch_size = max_batch_size
    _Handler.metrics = metrics
    return _Handler


def create_ingestion_api_server(
    *,
    host: str,
    port: int,
    coordinator: MultiStreamCoordinator,
    default_stream_id: str = "dc1",
    require_ingest_id: bool = True,
    max_batch_size: int = 128,
) -> IngestionAPIServer:
    """Create ingestion HTTP gateway server with deterministic behavior."""

    return IngestionAPIServer(
        (host, port),
        coordinator=coordinator,
        default_stream_id=default_stream_id,
        require_ingest_id=require_ingest_id,
        max_batch_size=max_batch_size,
    )
