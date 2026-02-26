Real DB Persistence Protocol (PostgreSQL)
=========================================

This protocol defines local development workflow for the Phase 8 real database
persistence backend.

Overview
--------

- Event log remains append-only source of truth.
- Replay ordering must use ``event_log.seq`` ascending.
- Snapshots are acceleration artifacts only; they never replace event truth.
- Payload and snapshot hashes use deterministic canonical serialization.

Docker Compose Usage
--------------------

1. Copy environment defaults:

   .. code-block:: bash

      cp .env.example .env

2. Start PostgreSQL:

   .. code-block:: bash

      docker compose up -d postgres

3. Verify readiness:

   .. code-block:: bash

      docker compose ps

Running Migrations
------------------

The migration file is:

- ``src/digital_twin/infrastructure/db/migrations/0001_init.sql``

Run migrations with a Python one-liner:

.. code-block:: bash

   python -c "from digital_twin.infrastructure.db.postgres import run_migrations; run_migrations()"

The DSN is read from ``DIGITAL_TWIN_DB_DSN`` (or fallback ``DATABASE_URL``).

Running Integration Tests
-------------------------

PostgreSQL integration tests are marked ``postgres`` and placed under
``tests/persistence``.

Run only persistence tests:

.. code-block:: bash

   pytest -m postgres tests/persistence

Run a single recovery equivalence test:

.. code-block:: bash

   pytest tests/persistence/test_pg_recovery_equivalence_vs_inmemory.py

Operational Cautions
--------------------

- **Always order replay reads by ``seq``**, never by ``created_at``.
- ``version_counter`` is a logical domain progression counter, not a DB ordering key.
- Snapshot retrieval uses maximum ``version_counter`` for a stream.
- Hash fields (``payload_sha256`` / ``snapshot_sha256``) are integrity checks for
  deterministic canonical bytes and corruption detection.


8.1 Hardening: Consistency + Idempotency
----------------------------------------

Schema invariants introduced (migration ``0002_hardening.sql``):

- ``event_log`` unique logical version per stream: ``UNIQUE(stream_id, version_counter)``.
- ``event_log`` idempotent ingest token per stream: ``UNIQUE(stream_id, ingest_id)``.
- replay/scan indexes:

  - ``idx_event_log_stream_seq`` on ``(stream_id, seq)``
  - ``idx_event_log_stream_version`` on ``(stream_id, version_counter)``

- snapshot latest lookup index:

  - ``idx_snapshot_latest`` on ``snapshot_store(stream_id, version_counter DESC)``

Append semantics:

- ``EventStorePG.append`` returns ``AppendResult.APPENDED`` or ``AppendResult.ALREADY_EXISTS``.
- If ``(stream_id, version_counter)`` is already claimed by another ingest,
  ``VersionConflictError`` is raised deterministically.
- Idempotency is based on ``(stream_id, ingest_id)``; duplicate identical append returns
  ``ALREADY_EXISTS`` explicitly (not silent success).

Batch semantics:

- ``append_batch`` is atomic and uses caller-provided order.
- Policy: fail-fast if any member returns ``ALREADY_EXISTS`` (explicitly signaled as batch error).

Snapshot pruning policy:

- ``SnapshotStorePG.prune_older_than(stream_id, keep_last_n=3)`` keeps the latest N snapshots
  ordered by ``version_counter`` and deletes older rows.
- Pruning is operational compaction only and does not change replay semantics.

Running both migrations:

.. code-block:: bash

   python -c "from digital_twin.infrastructure.db.postgres import run_migrations; run_migrations()"

The migration runner applies ``0001_init.sql`` followed by ``0002_hardening.sql``.

Phase 9E DB load notes
----------------------

When attributing bottlenecks, capture DB pooling and index/pruning configuration in
campaign ``manifest.yml`` notes. Compare:

- EventStorePG only vs EventStorePG + SnapshotStorePG.
- Snapshot interval/pruning policy impacts on write amplification.
- connection pool saturation against ingestion latency p95/p99.
