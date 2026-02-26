# Locust Ingestion Load Testing (HTTP Gateway)

Run against the ingestion HTTP gateway:

```bash
python -m digital_twin.presentation.ingestion_http_runner
```

Then execute Locust:

```bash
locust -f load_testing/locust_ingest/locustfile.py --host http://127.0.0.1:8091
```

Profiles: `steady_poisson_users`, `burst_pareto_users`, `multi_stream_scale`, `tick_heavy_infra`, `mixed_with_flows`.

All events include deterministic client-side `ingest_id` values derived from `(LOCUST_SEED, stream_id, sequence, event_type)`.
