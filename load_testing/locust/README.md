# Locust Load Testing (Phase 9E)

This directory contains a **local-only** Locust test suite for the Metrics API.

## Scope

The suite targets read-only endpoints:

- `GET /health`
- `GET /metrics`
- `GET /metrics/schema`
- `GET /metrics/streams`
- `GET /metrics/top`
- `GET /metrics/histograms`

It does not mutate deterministic domain state and does not bypass ingestion semantics.

## Quick start

1. Install dependencies:

```bash
pip install -r requirements-dev.txt
```

2. Copy and edit the config:

```bash
cp load_testing/locust/config.example.env load_testing/locust/.env
```

3. Run Locust (headless):

```bash
set -a && source load_testing/locust/.env && set +a
locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST" --users "$LOCUST_USERS" --spawn-rate "$LOCUST_SPAWN_RATE" --run-time "$LOCUST_RUN_TIME" --headless
```

4. Run with web UI:

```bash
set -a && source load_testing/locust/.env && set +a
locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST"
```

## Profiles

Choose with `LOCUST_PROFILE`:

- `steady_state_cache_hit`
- `burst_dashboard_refresh`
- `refresh_pressure`
- `mixed_observability`

See `profiles.py` for exact endpoint mix and behavior.

## Refresh forcing behavior

The current Metrics API does not expose a `?refresh=1` switch.

`refresh_pressure` therefore uses TTL-aligned waits when `REFRESH_TEST_MODE=1`:

- every `REFRESH_CYCLE_REQUESTS` requests, each user sleeps for
  `REFRESH_TTL_SECONDS + 0.05s`
- this increases cache refresh probability without adding mutation endpoints

## Result exports

Use Locust built-ins:

```bash
locust -f load_testing/locust/locustfile.py --host "$LOCUST_HOST" --headless \
  --users "$LOCUST_USERS" --spawn-rate "$LOCUST_SPAWN_RATE" --run-time "$LOCUST_RUN_TIME" \
  --csv load_testing/locust/results/run_01 --html load_testing/locust/results/run_01.html
```

A report template is available at `analysis_template.md`.
