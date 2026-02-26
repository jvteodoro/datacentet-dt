from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def postgres_dsn() -> str:
    return os.getenv("DIGITAL_TWIN_DB_DSN", "postgresql://digital_twin:digital_twin@localhost:5432/digital_twin")


@pytest.fixture(scope="session")
def ensure_postgres(postgres_dsn: str) -> None:
    psycopg = pytest.importorskip("psycopg")
    from digital_twin.infrastructure.db.postgres import run_migrations

    try:
        with psycopg.connect(postgres_dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as exc:  # pragma: no cover - env dependent
        pytest.skip(f"PostgreSQL unavailable for integration tests: {exc}")

    run_migrations(dsn=postgres_dsn)


@pytest.fixture(autouse=True)
def clean_tables(request: pytest.FixtureRequest, postgres_dsn: str) -> None:
    if request.node.get_closest_marker("postgres") is None:
        return

    request.getfixturevalue("ensure_postgres")

    import psycopg

    with psycopg.connect(postgres_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE event_log, snapshot_store RESTART IDENTITY")
        conn.commit()
