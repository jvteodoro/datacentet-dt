from __future__ import annotations

from load_testing.locust_ingest.profiles import SeededTrafficGenerator, build_profile_spec


def test_profile_generation_is_deterministic_for_same_seed() -> None:
    spec = build_profile_spec("mixed_with_flows")
    g1 = SeededTrafficGenerator(spec=spec, seed=99, source="locust", max_server_index=16)
    g2 = SeededTrafficGenerator(spec=spec, seed=99, source="locust", max_server_index=16)

    messages_1 = [g1.next_message() for _ in range(10)]
    messages_2 = [g2.next_message() for _ in range(10)]

    assert messages_1 == messages_2


def test_generated_messages_always_include_ingest_id() -> None:
    spec = build_profile_spec("steady_poisson_users")
    generator = SeededTrafficGenerator(spec=spec, seed=10, source="locust", max_server_index=8)

    for _ in range(20):
        message = generator.next_message()
        assert "ingest_id" in message
        assert isinstance(message["ingest_id"], str)
