Load Testing Strategy: HTTP-First vs Kafka Ingestion
=====================================================

Phase 9E.1 introduces HTTP ingestion load testing before Kafka ingestion load
campaigns. This sequence is intentional and methodologically constrained.

Theoretical motivation
----------------------

HTTP-first improves iteration speed and isolates application-level bottlenecks:

- JSON parsing and schema validation overhead.
- Domain transition + validation execution cost.
- Persistence and snapshot write-path cost.
- Gateway status/outcome distribution under concurrent clients.

Kafka-later preserves stream transport realism and isolates broker-consumer
bottlenecks that HTTP cannot measure:

- Broker partition throughput and replication pressure.
- Consumer group rebalance and partition assignment behavior.
- Commit policy, lag progression, and backpressure from offsets.
- Topic-level ordering guarantees across partitions.

Comparison table
----------------

+------------------------+-----------------------------+---------------------------------+
| Dimension              | HTTP Ingestion Path         | Kafka Ingestion Path            |
+========================+=============================+=================================+
| Protocol boundary      | Request/response API        | Broker + consumer loop          |
+------------------------+-----------------------------+---------------------------------+
| Primary bottlenecks    | Parser, domain, DB, API I/O | Broker, partitions, commits, lag|
+------------------------+-----------------------------+---------------------------------+
| Ordering semantics     | Per-request + stream route  | Partition order + stream key    |
+------------------------+-----------------------------+---------------------------------+
| DLQ behavior           | HTTP DLQ-like response only | Broker-backed DLQ topic         |
+------------------------+-----------------------------+---------------------------------+
| Rebalance behavior     | Not applicable              | Mandatory to evaluate           |
+------------------------+-----------------------------+---------------------------------+
| Iteration speed        | High                        | Moderate                        |
+------------------------+-----------------------------+---------------------------------+

What HTTP does not test
-----------------------

HTTP load tests do not evaluate partition rebalance safety, broker durability
behavior, or consumer lag dynamics. These are deferred to Kafka load scenarios
and should be interpreted as separate bottleneck families.

Methodological guidance
-----------------------

1. Use HTTP profiles to establish baseline p95/p99 ingestion latency envelopes.
2. Verify deterministic outcome distributions and idempotency behavior.
3. Run equivalent semantic workloads through Kafka ingestion for transport-aware
   bottleneck analysis.
4. Compare results without conflating protocol-specific bottlenecks.
