from __future__ import annotations

import os

from digital_twin.infrastructure.streaming.coordinator import MultiStreamCoordinator
from digital_twin.presentation.ingestion_http_api import create_ingestion_api_server


def main() -> None:
    """Run the ingestion HTTP API with environment-driven settings."""

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8091"))
    default_stream_id = os.getenv("DEFAULT_STREAM_ID", "dc1")
    require_ingest_id = os.getenv("REQUIRE_INGEST_ID", "1") == "1"
    max_batch_size = int(os.getenv("MAX_BATCH_SIZE", "128"))

    coordinator = MultiStreamCoordinator(default_stream_id=default_stream_id)
    server = create_ingestion_api_server(
        host=host,
        port=port,
        coordinator=coordinator,
        default_stream_id=default_stream_id,
        require_ingest_id=require_ingest_id,
        max_batch_size=max_batch_size,
    )
    print(f"ingestion_http_api listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
