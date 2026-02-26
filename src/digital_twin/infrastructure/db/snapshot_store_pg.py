from __future__ import annotations

import json
from dataclasses import asdict
from time import perf_counter
from typing import Any, Optional

from digital_twin.application.ports.snapshot_store import SnapshotStore
from digital_twin.domain.snapshot import TwinSnapshot

from .metrics import DBAdapterMetrics
from .postgres import bytes_sha256, canonical_json_bytes, connection_scope


class SnapshotStorePG(SnapshotStore):
    """Snapshot payload format: canonical JSON bytes with sorted keys."""

    def __init__(self, *, dsn: str | None = None, stream_id: str = "default", metrics: DBAdapterMetrics | None = None) -> None:
        self._dsn = dsn
        self._stream_id = stream_id
        self._metrics = metrics or DBAdapterMetrics()

    @property
    def metrics(self) -> DBAdapterMetrics:
        return self._metrics

    def save(self, snapshot: TwinSnapshot, stream_id: str | None = None, version_counter: int | None = None) -> None:
        row_stream_id = stream_id or self._stream_id
        row_version = version_counter if version_counter is not None else snapshot.version_counter
        snapshot_payload_bytes = canonical_json_bytes(asdict(snapshot))
        snapshot_hash = bytes_sha256(snapshot_payload_bytes)

        started = perf_counter()
        try:
            with connection_scope(dsn=self._dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO snapshot_store (
                            stream_id,
                            version_counter,
                            snapshot_payload,
                            snapshot_sha256
                        ) VALUES (%s, %s, %s, %s)
                        ON CONFLICT (stream_id, version_counter)
                        DO UPDATE SET
                            snapshot_payload = EXCLUDED.snapshot_payload,
                            snapshot_sha256 = EXCLUDED.snapshot_sha256
                        """,
                        (row_stream_id, row_version, snapshot_payload_bytes, snapshot_hash),
                    )
                conn.commit()
            self._metrics.record_snapshot_save_latency((perf_counter() - started) * 1000.0)
        except Exception:
            self._metrics.record_query_error()
            raise

    def load_latest(self, stream_id: str | None = None) -> Optional[TwinSnapshot]:
        row_stream_id = stream_id or self._stream_id
        started = perf_counter()
        try:
            with connection_scope(dsn=self._dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT snapshot_payload
                        FROM snapshot_store
                        WHERE stream_id = %s
                        ORDER BY version_counter DESC
                        LIMIT 1
                        """,
                        (row_stream_id,),
                    )
                    row = cur.fetchone()
            self._metrics.record_snapshot_load_latency((perf_counter() - started) * 1000.0)
        except Exception:
            self._metrics.record_query_error()
            raise

        if row is None:
            return None

        payload: dict[str, Any] = json.loads(bytes(row[0]).decode("utf-8"))
        return TwinSnapshot(**payload)

    def prune_older_than(self, *, stream_id: str | None = None, keep_last_n: int = 3) -> int:
        if keep_last_n <= 0:
            raise ValueError("keep_last_n must be > 0")

        row_stream_id = stream_id or self._stream_id
        try:
            with connection_scope(dsn=self._dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        DELETE FROM snapshot_store
                        WHERE stream_id = %s
                          AND version_counter < (
                              SELECT COALESCE(MIN(version_counter), -1)
                              FROM (
                                  SELECT version_counter
                                  FROM snapshot_store
                                  WHERE stream_id = %s
                                  ORDER BY version_counter DESC
                                  LIMIT %s
                              ) keep
                          )
                        """,
                        (row_stream_id, row_stream_id, keep_last_n),
                    )
                    deleted = cur.rowcount
                conn.commit()
                return deleted
        except Exception:
            self._metrics.record_query_error()
            raise
