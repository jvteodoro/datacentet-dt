from __future__ import annotations

import pytest

from domain.network import QueueState


def test_t1_flow_conservation_over_multiple_arrivals():
    queue = QueueState(capacity=10.0, service_rate=2.0)

    queue.apply_arrival(amount=5.0, timestamp=1.0)
    queue.apply_arrival(amount=4.0, timestamp=2.0)
    queue.apply_arrival(amount=7.0, timestamp=4.0)

    assert queue.total_arrived == pytest.approx(
        queue.total_served + queue.total_dropped + queue.current_depth
    )


def test_t2_capacity_limit_and_drop_accounting():
    queue = QueueState(capacity=3.0, service_rate=1.0)

    queue.apply_arrival(amount=5.0, timestamp=1.0)

    assert queue.current_depth == pytest.approx(3.0)
    assert queue.total_dropped == pytest.approx(2.0)


def test_t3_service_reduces_backlog_without_arrival():
    queue = QueueState(capacity=10.0, service_rate=2.0)
    queue.apply_arrival(amount=6.0, timestamp=1.0)

    queue.apply_arrival(amount=0.0, timestamp=3.0)

    assert queue.current_depth == pytest.approx(2.0)
    assert queue.total_served == pytest.approx(4.0)


def test_t4_non_negativity_when_time_step_is_large():
    queue = QueueState(capacity=10.0, service_rate=3.0)
    queue.apply_arrival(amount=4.0, timestamp=1.0)

    queue.apply_arrival(amount=0.0, timestamp=10.0)

    assert queue.current_depth == pytest.approx(0.0)
    assert queue.current_depth >= 0.0


def test_t5_temporal_violation_raises_error():
    queue = QueueState(capacity=10.0, service_rate=1.0)
    queue.apply_arrival(amount=1.0, timestamp=2.0)

    with pytest.raises(ValueError, match="temporal causality"):
        queue.apply_arrival(amount=1.0, timestamp=1.0)


def test_t6_determinism_for_same_arrival_sequence():
    sequence = [(5.0, 1.0), (2.0, 2.0), (10.0, 4.0), (1.0, 7.0)]

    def run_once() -> tuple[float, float, float, float]:
        queue = QueueState(capacity=8.0, service_rate=1.5)
        for amount, timestamp in sequence:
            queue.apply_arrival(amount=amount, timestamp=timestamp)

        return (
            queue.current_depth,
            queue.total_arrived,
            queue.total_served,
            queue.total_dropped,
        )

    first = run_once()
    second = run_once()

    assert first == second
