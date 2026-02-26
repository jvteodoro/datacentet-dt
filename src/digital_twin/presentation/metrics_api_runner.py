from __future__ import annotations

import os

from digital_twin.observability.registry import ObservabilityRegistry
from digital_twin.presentation.metrics_api import create_metrics_api_server


def run() -> None:
    host = os.getenv("METRICS_API_HOST", "0.0.0.0")
    port = int(os.getenv("METRICS_API_PORT", "8000"))
    mode = os.getenv("MODE", "LIVE")
    node_id = os.getenv("NODE_ID", "local-load-test")

    registry = ObservabilityRegistry(node_id=node_id)
    server = create_metrics_api_server(host=host, port=port, registry=registry, mode=mode)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
