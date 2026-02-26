from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from digital_twin.observability.cache import MetricsSnapshotCache
from digital_twin.observability.clock import DefaultClock
from digital_twin.observability.collector import SnapshotCollector
from digital_twin.observability.registry import ObservabilityRegistry
from digital_twin.observability.snapshot import snapshot_schema, stream_aggregates


class MetricsAPIHandler(BaseHTTPRequestHandler):
    cache: MetricsSnapshotCache
    mode: str

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return

        if self.path == "/metrics":
            snapshot = self.cache.get(mode=self.mode)
            self._send_json(HTTPStatus.OK, snapshot.to_dict())
            return

        if self.path == "/metrics/schema":
            snapshot = self.cache.get(mode=self.mode)
            payload = {"metrics": snapshot_schema(snapshot)}
            self._send_json(HTTPStatus.OK, payload)
            return

        if self.path == "/metrics/streams":
            snapshot = self.cache.get(mode=self.mode)
            self._send_json(HTTPStatus.OK, stream_aggregates(snapshot))
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class MetricsAPIServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], cache: MetricsSnapshotCache, mode: str = "LIVE") -> None:
        handler = _build_handler(cache=cache, mode=mode)
        super().__init__(server_address, handler)


def _build_handler(*, cache: MetricsSnapshotCache, mode: str) -> type[MetricsAPIHandler]:
    class _Handler(MetricsAPIHandler):
        pass

    _Handler.cache = cache
    _Handler.mode = mode.upper()
    return _Handler


def create_metrics_api_server(
    *,
    host: str,
    port: int,
    registry: ObservabilityRegistry,
    mode: str | None = None,
    node_id: str | None = None,
    ttl_ms: int | None = None,
    cache: MetricsSnapshotCache | None = None,
) -> MetricsAPIServer:
    mode_value = (mode or os.getenv("MODE") or "LIVE").upper()
    node_id_value = node_id if node_id is not None else os.getenv("NODE_ID")
    ttl_value = ttl_ms if ttl_ms is not None else int(os.getenv("METRICS_CACHE_TTL_MS", "200"))

    if cache is None:
        collector = SnapshotCollector(tuple(registry.providers), node_id=node_id_value or registry.node_id, clock=DefaultClock())
        cache = MetricsSnapshotCache(collector=collector, ttl_ms=ttl_value, clock=DefaultClock())
    return MetricsAPIServer((host, port), cache=cache, mode=mode_value)
