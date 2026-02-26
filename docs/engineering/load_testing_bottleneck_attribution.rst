Load Testing Bottleneck Attribution
===================================

Decision method
---------------

1. Domain bottleneck: domain-only scenario saturates CPU with low DB IO deltas.
2. DB bottleneck: DB scenario latency spikes and DB IO deltas increase materially.
3. Kafka transport/consumer bottleneck: lag grows while domain/DB signals remain stable.
4. HTTP transport bottleneck: HTTP p99 grows with low CPU and transport saturation signs.

Use ``load_testing/analysis/compare_http_vs_kafka.py`` and run artifacts as evidence.
