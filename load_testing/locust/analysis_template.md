# Phase 9E Locust Analysis Template

## Run metadata

- Date:
- Environment (CPU/RAM/OS):
- API deployment mode (local process/container):
- Metrics cache TTL (`METRICS_CACHE_TTL_MS`):
- Locust profile:
- Users / spawn rate / run time:

## Acceptance metrics

- Throughput (RPS):
- Error rate (%):
- `/metrics` p50 / p95 / p99 latency (ms):
- `/metrics/top` p50 / p95 / p99 latency (ms):
- Refresh spike max latency (ms):
- Sustained RPS floor met? (yes/no):

## Cache behavior characterization

- Cache-hit dominant window observations:
- Refresh pressure observations:
- Latency delta (hit vs refresh):

## Payload sizing

- `/metrics` average payload bytes:
- `/metrics/top` average payload bytes:
- `/metrics/histograms` average payload bytes:

## Notes / anomalies

- Warm-up duration used:
- Any transient startup errors:
- Outliers and suspected causes:
