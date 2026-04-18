#!/usr/bin/env bash
# Start lbc-api in Docker, run HTTP e2e tests against the live container API, then tear down.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT="${LBC_API_PORT:-8000}"
BASE_URL="http://127.0.0.1:${PORT}"

cleanup() {
  echo "==> docker compose down"
  docker compose down --remove-orphans
}
trap cleanup EXIT

echo "==> docker compose up -d --build lbc-api"
docker compose up -d --build lbc-api

if docker compose up --help 2>&1 | grep -q -- '--wait'; then
  docker compose up -d --wait lbc-api 2>/dev/null || true
fi

echo "==> waiting for ${BASE_URL}/health"
ok=0
for i in $(seq 1 90); do
  if curl -sf "${BASE_URL}/health" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 1
done
if [[ "$ok" != 1 ]]; then
  echo "ERROR: API did not become ready" >&2
  docker compose logs lbc-api --tail 80 >&2 || true
  exit 1
fi
echo -n "health: "
curl -sf "${BASE_URL}/health"
echo

echo "==> HTTP e2e from lbc-e2e container -> http://lbc-api:8000 (live Leboncoin via API)"
docker compose --profile e2e run --build --rm lbc-e2e

echo "==> e2e OK; shutting down (trap)"
