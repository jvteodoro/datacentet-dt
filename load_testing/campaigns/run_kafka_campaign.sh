#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RUN_ID="${RUN_ID:-kafka-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="$ROOT_DIR/load_testing/runs/$RUN_ID"
mkdir -p "$RUN_DIR/derived/plots"
PROFILE="${PROFILE:-uniform_streams}"
SEED="${SEED:-42}"
DURATION_S="${DURATION_S:-60}"
TARGET_RPS="${TARGET_RPS:-2000}"
TOPIC="${TOPIC:-digital-twin-ingest}"
BOOTSTRAP="${BOOTSTRAP:-127.0.0.1:9092}"
TARGET_PID="${TARGET_PID:-0}"
GIT_SHA="$(git -C "$ROOT_DIR" rev-parse HEAD)"
cat > "$RUN_DIR/manifest.yml" <<EOF
run_id: $RUN_ID
transport: kafka
target: $BOOTSTRAP
profile: $PROFILE
seed: $SEED
duration_s: $DURATION_S
target_rps: $TARGET_RPS
topic: $TOPIC
git_sha: $GIT_SHA
EOF
if [[ "$TARGET_PID" != "0" ]]; then
RESOURCE_PID="$TARGET_PID" RESOURCE_CSV="$RUN_DIR/resource_usage.csv" python "$ROOT_DIR/load_testing/telemetry/resource_sidecar.py" &
SIDECAR_PID=$!
else
SIDECAR_PID=""
fi
python -m load_testing.kafka_load.producer --profile "$PROFILE" --seed "$SEED" --duration-s "$DURATION_S" --target-rps "$TARGET_RPS" --topic "$TOPIC" --bootstrap-servers "$BOOTSTRAP" --out-jsonl "$RUN_DIR/producer_events.jsonl" > "$RUN_DIR/producer_metrics.json"
touch "$RUN_DIR/notes.md"
if [[ -n "$SIDECAR_PID" ]]; then kill "$SIDECAR_PID" || true; fi
