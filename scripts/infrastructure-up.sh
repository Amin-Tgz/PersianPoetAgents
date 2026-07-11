#!/usr/bin/env bash
# Start the whole stack (API + UI + MongoDB). Run from the repo root.
set -euo pipefail
docker compose up --build -d
