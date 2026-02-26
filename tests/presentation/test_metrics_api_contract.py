from __future__ import annotations

import json
import threading
import urllib.request

from digital_twin.domain.metrics import MetricsCollector
from digital_twin.observability.registry import DomainMetricsProvider, ObservabilityRegistry, StreamingMetricsProvider
from digital_twin.presentation.metrics_api import create_metrics_api_server
from digital_twin.infrastructure.streaming.streaming_metrics import StreamingMetricsCollector


def _get_json(url: str) -> tuple[str, dict[str, object]]:
    with urllib.request.urlopen(url, timeout=3) as response:  # noqa: S310 - local test server only
        body = response.read().decode("utf-8")
    return body, json.loads(body)


def test_metrics_api_contract_and_sorted_payload_keys() -> None:
    domain = MetricsCollector()
    domain.record_ingestion_latency(10)

    streaming = StreamingMetricsCollector()
    streaming.set_streams_active_gauge(2)
    streaming.record_eviction(reason="TTL")
    streaming.record_outcome(status="APPLIED")
    streaming.set_kafka_lag_last(4)

    registry = ObservabilityRegistry(node_id="node-api")
    registry.register(DomainMetricsProvider(domain))
    registry.register(StreamingMetricsProvider(streaming))

    server = create_metrics_api_server(host="127.0.0.1", port=0, registry=registry, mode="LIVE")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base = f"http://127.0.0.1:{server.server_port}"
        metrics_body, metrics = _get_json(f"{base}/metrics")
        _, schema = _get_json(f"{base}/metrics/schema")
        _, streams = _get_json(f"{base}/metrics/streams")
        _, topk = _get_json(f"{base}/metrics/top")
        _, histograms = _get_json(f"{base}/metrics/histograms")

        assert metrics["mode"] == "LIVE"
        assert metrics["node_id"] == "node-api"
        assert metrics["produced_at_utc"] is not None
        assert metrics["snapshot_age_ms"] is not None
        assert "observability.cache_refresh_errors_total" in metrics["metrics"]
        assert metrics_body == json.dumps(metrics, separators=(",", ":"), sort_keys=True)
        assert list(metrics["metrics"].keys()) == sorted(metrics["metrics"].keys())

        assert "scalar_metrics" in schema
        assert isinstance(schema["scalar_metrics"], list)
        assert isinstance(schema["topk"], list)
        assert isinstance(schema["histograms"], list)
        assert any(item["name"] == "domain.events_processed_total" for item in schema["scalar_metrics"])

        assert streams["active_streams"] == 2
        assert streams["evictions_total"] == 1
        assert streams["outcomes_total"]["APPLIED"] == 1
        assert streams["kafka_lag_last"] == 4

        assert topk["limit"] > 0
        assert isinstance(topk["topk"], dict)

        assert isinstance(histograms["histograms"], dict)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
