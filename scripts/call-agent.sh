#!/usr/bin/env bash
# Smoke-test a poet directly (bypasses the UI). Run from the repo root in Git Bash.
# Infrastructure (MongoDB) must be up. Persian text works natively in Git Bash.
#   bash scripts/call-agent.sh                    # hafez, default greeting
#   bash scripts/call-agent.sh saadi              # another poet
#   bash scripts/call-agent.sh hafez "دیوان تو چه نام دارد؟"
set -euo pipefail

POET_ID="${1:-hafez}"
QUERY="${2:-سلام! خودت را معرفی کن.}"
IMAGE="${IMAGE:-persianpoetagents-api:latest}"
HOST_DIR="$(pwd -W 2>/dev/null || pwd)"

MSYS_NO_PATHCONV=1 docker run --rm \
  --network=philoagents-network \
  -e UV_INDEX_URL=https://pypi.org/simple \
  --env-file philoagents-api/.env \
  -v "$HOST_DIR/philoagents-api/data:/app/data" \
  -v "$HOST_DIR/philoagents-api/src/philoagents:/app/philoagents" \
  -v "$HOST_DIR/philoagents-api/tools:/app/tools" \
  "$IMAGE" uv run python -m tools.call_agent --philosopher-id "$POET_ID" --query "$QUERY"
