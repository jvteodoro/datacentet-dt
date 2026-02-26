from __future__ import annotations

from digital_twin.infrastructure.db.postgres import canonical_json_bytes, canonical_payload_sha256


def test_payload_hash_is_stable_and_order_invariant() -> None:
    payload_a = {"stream": "A", "nested": {"z": 3, "a": 1}, "values": [1, 2, 3]}
    payload_b = {"values": [1, 2, 3], "nested": {"a": 1, "z": 3}, "stream": "A"}

    assert canonical_json_bytes(payload_a) == canonical_json_bytes(payload_b)
    assert canonical_payload_sha256(payload_a) == canonical_payload_sha256(payload_b)
