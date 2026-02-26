Kafka Streaming Ingestion Protocol
==================================

Phase 9A introduces a Kafka infrastructure adapter that feeds telemetry events
into ``DataCenterTwin.ingest_event`` while preserving deterministic domain semantics.

Local stack boot
----------------

1. Copy defaults:

   .. code-block:: bash

      cp .env.stack.example .env.stack

2. Start unified services:

   .. code-block:: bash

      docker compose -f docker-compose.stack.yml --env-file .env.stack up -d

3. Run DB migrations:

   .. code-block:: bash

      DIGITAL_TWIN_DB_DSN=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB \
      python -c "from digital_twin.infrastructure.db.postgres import run_migrations; run_migrations()"

Create topics
-------------

.. code-block:: bash

   docker exec -it dt-kafka kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists --topic dt.telemetry --partitions 1 --replication-factor 1
   docker exec -it dt-kafka kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists --topic dt.telemetry.dlq --partitions 1 --replication-factor 1
   docker exec -it dt-kafka kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists --topic dt.control --partitions 1 --replication-factor 1

Canonical telemetry message
---------------------------

.. code-block:: json

   {
     "stream_id": "dc1",
     "ingest_id": "uuid-string",
     "source": "iot_adapter_name",
     "source_time_utc": "2025-01-01T00:00:00Z",
     "event_type": "AddNode|AddLink|FlowStarted|FlowEnded|WorkloadStarted|WorkloadEnded|Tick",
     "payload": {}
   }

Validation/normalization notes:

- ``ingest_id`` must parse as UUID; if absent, a new UUID is generated at ingest time.
- Required payload fields are validated per event type before mapping.
- Kafka partition/offset metadata is attached as observational payload metadata only.

Run consumer locally
--------------------

.. code-block:: bash

   PYTHONPATH=src python -c "from digital_twin.infrastructure.streaming import KafkaSettings, KafkaConsumerAdapter, MultiStreamCoordinator; settings = KafkaSettings.from_env(); adapter = KafkaConsumerAdapter(settings=settings, coordinator=MultiStreamCoordinator(default_stream_id=settings.stream_id)); adapter.poll_forever()"

Operational semantics
---------------------

- Consumer is single-threaded and processes records sequentially.
- Offset commit occurs only after ingest handling returns successfully.
- Duplicate ingest token handling uses DB idempotency signal:

  - ``AppendResult.APPENDED`` => normal progress.
  - ``AppendResult.ALREADY_EXISTS`` => duplicate, skip state mutation, commit offset.

- ``VersionConflictError`` is treated as stream divergence and is raised (consumer stops).
- Validation/transition errors are sent to ``DLQ`` with original payload + reason, then offset is committed.

Kafka-marked tests
------------------

.. code-block:: bash

   PYTHONPATH=src pytest -q tests/streaming -m kafka


Phase 9C: Hyperscale Partitioning and Multi-Stream Semantics
-------------------------------------------------------------

Partition key policy
~~~~~~~~~~~~~~~~~~~~

- Telemetry producer must publish with ``key = stream_id``.
- ``stream_id`` in the message body is mandatory and treated as the authoritative
  routing key by the ingestion coordinator.

Consumer group policy and scaling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Use Kafka consumer groups to scale horizontally across partitions.
- Configure multiple consumer instances with the same ``group_id`` and distinct
  ``client_id`` values.
- Keep ``enable_auto_commit = false`` and commit offsets only after:

  - ``APPLIED``
  - ``DUPLICATE``
  - ``DLQ``

- On ``VERSION_CONFLICT`` the consumer stops and does **not** commit the
  conflicting offset.

Determinism guarantee
~~~~~~~~~~~~~~~~~~~~~

- FIFO is guaranteed **per stream** when all events for that ``stream_id`` map
  to the same Kafka partition and are consumed in-order by the assigned
  consumer instance.
- This phase does **not** guarantee global cross-stream ordering.

Why one twin per stream
~~~~~~~~~~~~~~~~~~~~~~~

- ``DataCenterTwin`` state is stream-scoped.
- ``MultiStreamCoordinator`` lazily creates one twin per ``stream_id`` and
  isolates per-stream state evolution and idempotency signaling.

Operational notes
~~~~~~~~~~~~~~~~~

- Scale by increasing topic partitions and consumer instances together.
- Monitor partition lag and rebalance frequency per consumer group.
- Keep partition count >= expected active stream concurrency.
- ``ingest_id`` behavior remains valid: when missing, consumer generates UUID
  at ingest boundary; persisted ingest IDs remain the replay/idempotency source
  of truth.


Phase 9C.1: Hardening (Eviction, Rebalance Safety, Metrics Side-Channel)
------------------------------------------------------------------------

Coordinator eviction semantics (TTL + LRU)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``MultiStreamCoordinator`` keeps in-memory stream twins bounded by:

  - ``max_active_streams`` hard cap
  - ``stream_ttl_seconds`` inactivity TTL (monotonic-clock based)
  - ``eviction_policy=LRU``

- TTL uses ``time.monotonic()`` and is operational only (no effect on domain
  event timestamps or replay logic).
- Eviction only removes in-memory twin instances. Event truth remains in
  PostgreSQL ``event_log`` and stream recovery remains possible via
  snapshot + tail replay.

Rebalance safety
~~~~~~~~~~~~~~~~

- Consumer tracks partition revocation/assignment and must not process records
  from revoked/unassigned partitions.
- On revoke, the adapter commits only already-processed offsets and stops
  processing revoked partitions immediately.
- No background processing threads are used after revoke.
- For client libraries lacking complete callback support, assignment-set checks
  in poll/handle path provide conservative safety.

Hot Stream Mitigation (Scale-Out by Substreams)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- If a single stream saturates one partition, split to substreams such as:

  - ``dc1.rack12`` and ``dc1.rack13``
  - ``dc1.switchA`` and ``dc1.switchB``

- Each substream is an independent ``stream_id`` with its own partition key,
  twin instance, and DB stream namespace.
- Determinism is preserved per substream (FIFO per stream/substream).
- Global ordering across substreams is intentionally **not** guaranteed.

Streaming metrics side-channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Coordinator/consumer publish observational metrics only:

  - active stream gauge
  - eviction totals (TTL/capacity)
  - ingestion outcome counters
  - coordinator handle latency (rolling)
  - optional lag hint

- Metrics never alter domain transitions, validation, or replay semantics.
