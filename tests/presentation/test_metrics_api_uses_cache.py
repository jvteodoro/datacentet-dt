from __future__ import annotations

import json
import threading
import urllib.request

from digital_twin.observability.cache import MetricsSnapshotCache
from digital_twin.observability.clock import Clock
from digital_twin.observability.collector import SnapshotCollector
from digital_twin.observability.model import Histogram, MetricKind, MetricPoint, TopKEntry
from digital_twin.observability.registry import ObservabilityRegistry
from digital_twin.presentation.metrics_api import create_metrics_api_server


class _FakeClock(Clock):
    def __init__(self) -> None:
        self.monotonic = 0.0

    def now_monotonic(self) -> float:
        return self.monotonic

    def now_utc_rfc3339(self) -> str:
        return "2026-01-01T00:00:00Z"


class _Provider:
    def __init__(self) -> None:
        self.calls = 0

    def collect_metrics(self) -> dict[str, MetricPoint]:
        self.calls += 1
        return {"z": MetricPoint(kind=MetricKind.COUNTER, value=self.calls)}

    def collect_topk(self) -> dict[str, tuple[TopKEntry, ...]]:
        return {"top.links.by_backlog": (TopKEntry(id="link-0", value=1.0),)}

    def collect_histograms(self) -> dict[str, Histogram]:
        return {"hist.net.backlog": Histogram(bin_edges=(0.0, 1.0), counts=(1,))}


def _get_json(url: str) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=3) as response:  # noqa: S310 local server
        return json.loads(response.read().decode("utf-8"))


def test_metrics_endpoint_uses_cache_not_full_refresh_per_request() -> None:
    provider = _Provider()
    clock = _FakeClock()
    collector = SnapshotCollector((provider,), node_id="node-cache", clock=clock)
    cache = MetricsSnapshotCache(collector=collector, ttl_ms=200, clock=clock)

    server = create_metrics_api_server(
        host="127.0.0.1",
        port=0,
        registry=ObservabilityRegistry(node_id="node-cache"),
        mode="LIVE",
        cache=cache,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base = f"http://127.0.0.1:{server.server_port}"
        for _ in range(120):
            _get_json(f"{base}/metrics")
            _get_json(f"{base}/metrics/top")
            _get_json(f"{base}/metrics/histograms")

        assert provider.calls <= 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
