# Campaign scripts

- `run_http_campaign.sh`: deterministic HTTP locust run + manifest + resource sidecar.
- `run_kafka_campaign.sh`: deterministic Kafka producer run + manifest + resource sidecar.
- `run_compare_campaign.sh`: compares one HTTP run and one Kafka run.
- `run_rebalance_stress.sh`: Kafka stress profile runner with rebalance action annotations.

Each script writes artifacts under `load_testing/runs/<run_id>/`.
