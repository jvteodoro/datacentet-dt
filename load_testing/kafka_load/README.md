# Kafka ingestion load suite

This suite reuses the same deterministic logical generator as HTTP (`load_testing.locust_ingest.seeded_generator`).

## Run

```bash
python -m load_testing.kafka_load.producer --profile uniform_streams --seed 42 --topic digital-twin-ingest
```

- Partition key is `stream_id`.
- Use `--out-jsonl` to persist generated payloads for reproducibility checks.
