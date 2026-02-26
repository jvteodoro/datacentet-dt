from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

from digital_twin.domain.twin import DataCenterTwin
from digital_twin.infrastructure.streaming.coordinator import MultiStreamCoordinator
from digital_twin.presentation.ingestion_http_api import create_ingestion_api_server


def _post_json(url: str, payload: object) -> tuple[int, str, dict[str, object]]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3) as response:  # noqa: S310 - local test server only
            body = response.read().decode("utf-8")
            return response.status, body, json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        return exc.code, body, json.loads(body)


def test_ingestion_http_contract_and_sorted_payload_keys() -> None:
    coordinator = MultiStreamCoordinator(default_stream_id="dc1", twin_factory=lambda _stream_id: DataCenterTwin())
    server = create_ingestion_api_server(host="127.0.0.1", port=0, coordinator=coordinator, require_ingest_id=True, max_batch_size=4)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base = f"http://127.0.0.1:{server.server_port}"
        status_ok, body_ok, payload_ok = _post_json(
            f"{base}/ingest",
            {
                "stream_id": "dc1",
                "ingest_id": "11111111-1111-1111-1111-111111111111",
                "source": "test",
                "source_time_utc": "2026-01-01T00:00:00Z",
                "event_type": "AddNode",
                "payload": {"node_id": "A"},
            },
        )
        assert status_ok == 200
        assert payload_ok["status"] == "APPLIED"
        assert body_ok == json.dumps(payload_ok, separators=(",", ":"), sort_keys=True)

        status_bad, _body_bad, payload_bad = _post_json(
            f"{base}/ingest",
            {
                "stream_id": "dc1",
                "source": "test",
                "source_time_utc": "2026-01-01T00:00:00Z",
                "event_type": "AddNode",
                "payload": {"node_id": "A"},
            },
        )
        assert status_bad == 400
        assert payload_bad["status"] == "DLQ"
        assert "dlq_reason" in payload_bad

        status_batch, _body_batch, payload_batch = _post_json(
            f"{base}/ingest/batch",
            [
                {
                    "stream_id": "dc1",
                    "ingest_id": "11111111-1111-1111-1111-111111111113",
                    "source": "test",
                    "source_time_utc": "2026-01-01T00:00:02Z",
                    "event_type": "AddNode",
                    "payload": {"node_id": "C"},
                },
                {
                    "stream_id": "dc1",
                    "ingest_id": "11111111-1111-1111-1111-111111111112",
                    "source": "test",
                    "source_time_utc": "2026-01-01T00:00:01Z",
                    "event_type": "AddNode",
                    "payload": {"node_id": "B"},
                },
            ],
        )
        assert status_batch == 200
        assert payload_batch["batch_ordering"] == "sorted(source_time_utc, ingest_id)"
        assert [item["ingest_id"] for item in payload_batch["items"]] == [
            "11111111-1111-1111-1111-111111111112",
            "11111111-1111-1111-1111-111111111113",
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
