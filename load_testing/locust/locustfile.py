from __future__ import annotations

from gevent import sleep as gevent_sleep
from locust import HttpUser, between, events, task

from profiles import (
    PROFILE_BURST_DASHBOARD_REFRESH,
    PROFILE_REFRESH_PRESSURE,
    build_profile_spec,
    runtime_config_from_env,
)

RUNTIME = runtime_config_from_env()
PROFILE = build_profile_spec(RUNTIME.profile)


@events.init_command_line_parser.add_listener
def _(parser) -> None:
    parser.set_defaults(stop_timeout=RUNTIME.stop_timeout)


class MetricsAPIUser(HttpUser):
    wait_time = between(0.05, 0.25)
    request_count = 0

    def on_start(self) -> None:
        if RUNTIME.headers:
            self.client.headers.update(RUNTIME.headers)

    @task
    def run_profile(self) -> None:
        for endpoint in PROFILE.endpoints:
            if endpoint.weight <= 0:
                continue
            if PROFILE.name == PROFILE_BURST_DASHBOARD_REFRESH:
                for _ in range(PROFILE.burst_size):
                    self._get(endpoint.path, endpoint.name)
                    self.request_count += 1
                continue

            for _ in range(endpoint.weight):
                self._get(endpoint.path, endpoint.name)
                self.request_count += 1
                self._apply_refresh_pressure_wait()

    def _apply_refresh_pressure_wait(self) -> None:
        if PROFILE.name != PROFILE_REFRESH_PRESSURE:
            return
        if not RUNTIME.refresh_test_mode:
            return
        cycle = PROFILE.refresh_cycle_requests
        if cycle <= 0:
            return
        if self.request_count > 0 and self.request_count % cycle == 0:
            gevent_sleep(max(RUNTIME.refresh_ttl_seconds + 0.05, 0.05))

    def _get(self, path: str, name: str) -> None:
        self.client.get(path, name=name)
