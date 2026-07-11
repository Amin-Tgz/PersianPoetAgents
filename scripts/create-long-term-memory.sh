#!/usr/bin/env bash
# Rebuilds the long-term memory: clears the collection, re-ingests Wikipedia + Ganjoor,
# and recreates the hybrid vector index with the configured EMBEDDING_DIM.
# Run from the repo root in Git Bash AFTER download-ganjoor.sh, with LM Studio serving
# the embedding model. Infrastructure (MongoDB) must be up.
#   bash scripts/create-long-term-memory.sh
set -euo pipefail

IMAGE="${IMAGE:-persianpoetagents-api:latest}"
HOST_DIR="$(pwd -W 2>/dev/null || pwd)"

MSYS_NO_PATHCONV=1 docker run --rm \
  --network=philoagents-network \
  -e UV_INDEX_URL=https://pypi.org/simple \
  --env-file philoagents-api/.env \
  -v "$HOST_DIR/philoagents-api/data:/app/data" \
  -v "$HOST_DIR/philoagents-api/src/philoagents:/app/philoagents" \
  -v "$HOST_DIR/philoagents-api/tools:/app/tools" \
  "$IMAGE" uv run python -m tools.create_long_term_memory
