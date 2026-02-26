#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RUN_ID="${RUN_ID:-rebalance-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="$ROOT_DIR/load_testing/runs/$RUN_ID"
mkdir -p "$RUN_DIR/derived/plots"
PROFILE="${PROFILE:-rebalance_churn}"
REBALANCE_AT_S="${REBALANCE_AT_S:-30}"
cat > "$RUN_DIR/manifest.yml" <<EOF
run_id: $RUN_ID
transport: kafka
profile: $PROFILE
rebalance_at_s: $REBALANCE_AT_S
rebalance_actions:
  - action: stop_consumer
    at_s: $REBALANCE_AT_S
  - action: start_consumer
    at_s: $((REBALANCE_AT_S+10))
EOF
{
  echo "# Rebalance notes"
  echo "- $(date -u +%FT%TZ): starting producer"
  echo "- $(date -u +%FT%TZ): scheduled stop consumer at ${REBALANCE_AT_S}s"
} > "$RUN_DIR/notes.md"
python -m load_testing.kafka_load.producer --profile "$PROFILE" --duration-s 120 --target-rps 2500 --out-jsonl "$RUN_DIR/producer_events.jsonl" > "$RUN_DIR/producer_metrics.json"
