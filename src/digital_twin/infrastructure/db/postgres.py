from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import psycopg
from psycopg import Connection


DEFAULT_DB_ENV_KEY = "DIGITAL_TWIN_DB_DSN"


class PostgresConnectionFactory:
    """Connection provider with optional psycopg_pool backing."""

    def __init__(self, *, dsn: str | None = None, min_size: int = 1, max_size: int = 4) -> None:
        self._dsn = dsn or resolve_dsn()
        self._pool = None
        try:
            from psycopg_pool import ConnectionPool

            self._pool = ConnectionPool(conninfo=self._dsn, min_size=min_size, max_size=max_size, open=True)
        except Exception:
            self._pool = None

    @contextmanager
    def connection(self) -> Iterator[Connection[Any]]:
        if self._pool is not None:
            with self._pool.connection() as conn:
                yield conn
            return

        with psycopg.connect(self._dsn) as conn:
            yield conn


_default_factory: PostgresConnectionFactory | None = None


def _json_compatible(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_compatible(val) for key, val in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_json_compatible(item) for item in value]
    return value


def canonical_json_bytes(payload: Any) -> bytes:
    canonical_payload = _json_compatible(payload)
    text = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def canonical_payload_sha256(payload: Any) -> bytes:
    return hashlib.sha256(canonical_json_bytes(payload)).digest()


def bytes_sha256(payload: bytes) -> bytes:
    return hashlib.sha256(payload).digest()


def resolve_dsn() -> str:
    dsn = os.getenv(DEFAULT_DB_ENV_KEY) or os.getenv("DATABASE_URL")
    if not dsn:
        raise ValueError(f"Missing database DSN. Set {DEFAULT_DB_ENV_KEY} or DATABASE_URL.")
    return dsn


def get_connection_factory(*, dsn: str | None = None) -> PostgresConnectionFactory:
    global _default_factory
    if dsn is not None:
        return PostgresConnectionFactory(dsn=dsn)
    if _default_factory is None:
        _default_factory = PostgresConnectionFactory(dsn=resolve_dsn())
    return _default_factory


def connect(*, dsn: str | None = None) -> Connection[Any]:
    return psycopg.connect(dsn or resolve_dsn())


@contextmanager
def connection_scope(*, dsn: str | None = None) -> Iterator[Connection[Any]]:
    with get_connection_factory(dsn=dsn).connection() as conn:
        yield conn


def run_migrations(*, dsn: str | None = None) -> None:
    migration_dir = Path(__file__).resolve().parent / "migrations"
    migration_files = sorted(migration_dir.glob("*.sql"))

    with connection_scope(dsn=dsn) as conn:
        with conn.cursor() as cur:
            for migration_file in migration_files:
                cur.execute(migration_file.read_text(encoding="utf-8"))
        conn.commit()
