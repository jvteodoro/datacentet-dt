#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
RUN_ID="${RUN_ID:-http-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="$ROOT_DIR/load_testing/runs/$RUN_ID"
mkdir -p "$RUN_DIR/derived/plots"

PROFILE="${PROFILE:-steady_poisson_users}"
SEED="${SEED:-42}"
USERS="${USERS:-10}"
SPAWN_RATE="${SPAWN_RATE:-2}"
DURATION="${DURATION:-60s}"
HOST="${HOST:-http://127.0.0.1:8091}"
TARGET_PID="${TARGET_PID:-0}"
GIT_SHA="$(git -C "$ROOT_DIR" rev-parse HEAD)"

cat > "$RUN_DIR/manifest.yml" <<EOF
run_id: $RUN_ID
transport: http
target: $HOST
profile: $PROFILE
seed: $SEED
users: $USERS
spawn_rate: $SPAWN_RATE
duration: $DURATION
git_sha: $GIT_SHA
require_ingest_id: ${LOCUST_REQUIRE_INGEST_ID:-true}
duplicate_rate: ${LOCUST_DUPLICATE_RATE:-0.0}
num_nodes: ${LOCUST_NUM_NODES:-200}
num_links: ${LOCUST_NUM_LINKS:-400}
num_servers: ${LOCUST_NUM_SERVERS:-100}
EOF

if [[ "$TARGET_PID" != "0" ]]; then
  RESOURCE_PID="$TARGET_PID" RESOURCE_CSV="$RUN_DIR/resource_usage.csv" \
    python "$ROOT_DIR/load_testing/telemetry/resource_sidecar.py" &
  SIDECAR_PID=$!
else
  SIDECAR_PID=""
fi

LOCUST_SEED="$SEED" LOCUST_INGEST_PROFILE="$PROFILE" \
locust -f "$ROOT_DIR/load_testing/locust_ingest/locustfile.py" --headless --host "$HOST" \
  --users "$USERS" --spawn-rate "$SPAWN_RATE" --run-time "$DURATION" \
  --csv "$RUN_DIR/locust" --csv-full-history

[[ -f "$RUN_DIR/locust_stats.csv" ]] || mv "$RUN_DIR"/locust*_stats.csv "$RUN_DIR/locust_stats.csv" 2>/dev/null || true
[[ -f "$RUN_DIR/locust_failures.csv" ]] || mv "$RUN_DIR"/locust*_failures.csv "$RUN_DIR/locust_failures.csv" 2>/dev/null || true

if [[ -n "$SIDECAR_PID" ]]; then
  kill "$SIDECAR_PID" || true
fi

touch "$RUN_DIR/notes.md"
echo "HTTP campaign completed: $RUN_DIR"
