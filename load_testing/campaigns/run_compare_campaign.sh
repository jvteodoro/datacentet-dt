#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
HTTP_RUN="${1:?http run dir required}"
KAFKA_RUN="${2:?kafka run dir required}"
python "$ROOT_DIR/load_testing/analysis/compare_http_vs_kafka.py" --http-run "$HTTP_RUN" --kafka-run "$KAFKA_RUN"
