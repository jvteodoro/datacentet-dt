from __future__ import annotations

from gevent import sleep as gevent_sleep
from locust import HttpUser, between, task

from load_testing.locust_ingest.profiles import build_profile_spec, runtime_config_from_env
from load_testing.locust_ingest.seeded_generator import SeededTelemetryGenerator

RUNTIME = runtime_config_from_env()
PROFILE = build_profile_spec(RUNTIME.profile)


class IngestionGatewayUser(HttpUser):
    wait_time = between(0.001, 0.01)

    def on_start(self) -> None:
        user_seed = RUNTIME.seed + int(self.environment.runner.user_count)
        self.generator = SeededTelemetryGenerator(
            profile=PROFILE,
            infra_size=RUNTIME.infra_size,
            seed=user_seed,
            source=RUNTIME.source,
            require_ingest_id=RUNTIME.require_ingest_id,
            duplicate_rate=RUNTIME.duplicate_rate,
        )

    @task
    def ingest_event(self) -> None:
        message = self.generator.next_message()
        with self.client.post("/ingest", json=message, name=f"ingest:{message['event_type']}", catch_response=True) as response:
            if response.status_code not in (200, 409):
                response.failure(f"unexpected status={response.status_code} body={response.text}")
        gevent_sleep(self.generator.next_interarrival_seconds())
