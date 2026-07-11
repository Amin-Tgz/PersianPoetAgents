#!/usr/bin/env bash
# Downloads poem corpora from api.ganjoor.net into philoagents-api/data/ganjoor/.
# Run from the repo root in Git Bash. Examples:
#   bash scripts/download-ganjoor.sh                            # all 7 poets, default limit
#   bash scripts/download-ganjoor.sh --poet hafez --max-poems 5 # quick smoke test
#   IMAGE=my-other-image bash scripts/download-ganjoor.sh       # override image name
set -euo pipefail

IMAGE="${IMAGE:-persianpoetagents-api:latest}"

# Git Bash: pwd -W gives a Windows-style path (D:/...) that Docker Desktop understands.
HOST_DIR="$(pwd -W 2>/dev/null || pwd)"

# MSYS_NO_PATHCONV=1 stops Git Bash from mangling the /app/... container paths.
MSYS_NO_PATHCONV=1 docker run --rm \
  -e UV_INDEX_URL=https://pypi.org/simple \
  --env-file philoagents-api/.env \
  -v "$HOST_DIR/philoagents-api/data:/app/data" \
  -v "$HOST_DIR/philoagents-api/src/philoagents:/app/philoagents" \
  -v "$HOST_DIR/philoagents-api/tools:/app/tools" \
  "$IMAGE" uv run python -m tools.download_ganjoor "$@"
