# Locust Ingestion Load Testing (HTTP Gateway)

Profiles: `steady_poisson_users`, `burst_pareto_users`, `multi_stream_scale`, `tick_heavy_infra`, `mixed_with_flows`.

Determinism contract:
- Same seed => same per-stream logical sequence (`stream_id`, event order, ingest_id if enabled).
- `ingest_id` is enabled by default (`LOCUST_REQUIRE_INGEST_ID=true`).
- Duplicate injection is explicit (`LOCUST_DUPLICATE_RATE`, default `0.0`).

Infrastructure sizing knobs:
- `LOCUST_NUM_NODES`
- `LOCUST_NUM_LINKS`
- `LOCUST_NUM_SERVERS`

Use `load_testing/campaigns/run_http_campaign.sh` to capture full run artifacts.
