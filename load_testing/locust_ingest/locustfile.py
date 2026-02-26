from __future__ import annotations

from gevent import sleep as gevent_sleep
from locust import HttpUser, between, task

from profiles import SeededTrafficGenerator, build_profile_spec, runtime_config_from_env

RUNTIME = runtime_config_from_env()
PROFILE = build_profile_spec(RUNTIME.profile)


class IngestionGatewayUser(HttpUser):
    wait_time = between(0.001, 0.01)

    def on_start(self) -> None:
        user_seed = RUNTIME.seed + int(self.environment.runner.user_count)
        self.generator = SeededTrafficGenerator(
            spec=PROFILE,
            seed=user_seed,
            source=RUNTIME.source,
            max_server_index=RUNTIME.max_server_index,
        )

    @task
    def ingest_event(self) -> None:
        message = self.generator.next_message()
        with self.client.post("/ingest", json=message, name=f"ingest:{message['event_type']}", catch_response=True) as response:
            if response.status_code not in (200, 409):
                response.failure(f"unexpected status={response.status_code} body={response.text}")
        gevent_sleep(self.generator.next_interarrival_seconds())
