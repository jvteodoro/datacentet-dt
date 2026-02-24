import pytest
from hypothesis import assume, given, strategies as st
# test/domain/properties/test_t_properties.py

"""
| Invariante | Essência                               |
| ---------- | -------------------------------------- |
| **T1**     | Existência de contexto temporal válido |
| **T2**     | Monotonicidade temporal                |
| **T3**     | Causalidade (sem uso do futuro)        |
| **T4**     | Alinhamento temporal ao combinar dados |

"""

times = st.lists(st.integers(min_value=0), min_size=1)
monotonic_times = st.lists(
    st.integers(min_value=0),
    min_size=1
).map(lambda xs: sorted(xs))
def with_regression(xs):
    if len(xs) < 2:
        return xs
    xs = list(xs)
    xs[1] = max(0, xs[0] - 1)
    return xs

regressive_times = st.lists(
    st.integers(min_value=1),
    min_size=2
).map(with_regression)

@given(t=st.none())
def test_T1_update_requires_explicit_timestamp(t):
    class Component:
        def update(self, time):
            if time is None:
                raise Exception("TemporalViolation")

    c = Component()
    with pytest.raises(Exception):
        c.update(t)

@given(ts=monotonic_times)
def test_T2_monotonic_sequences_are_accepted(ts):
    last = -1
    for t in ts:
        assert t >= last
        last = t

@given(ts=regressive_times)
def test_T2_regressive_sequences_are_rejected(ts):
    last = ts[0]
    violated = False
    for t in ts[1:]:
        if t < last:
            violated = True
        last = t
    assert violated

@given(
    current=st.integers(min_value=0),
    future=st.integers(min_value=1)
)
def test_T3_future_data_is_not_usable(current, future):
    assume(future > current)

    def use_data(now, data_time):
        if data_time > now:
            raise Exception("TemporalViolation")

    with pytest.raises(Exception):
        use_data(current, future)

@given(
    t_state=st.integers(min_value=0),
    t_obs=st.integers(min_value=0)
)
def test_T4_temporal_alignment_required(t_state, t_obs):
    def combine(state_time, obs_time):
        if abs(state_time - obs_time) > 0:
            raise Exception("TemporalViolation")

    if t_state != t_obs:
        with pytest.raises(Exception):
            combine(t_state, t_obs)

@given(
    parent_t=st.integers(min_value=0),
    child_t=st.integers(min_value=0)
)
def test_T_parent_cannot_see_child_future(parent_t, child_t):
    if child_t > parent_t:
        with pytest.raises(Exception):
            raise Exception("TemporalViolation")
