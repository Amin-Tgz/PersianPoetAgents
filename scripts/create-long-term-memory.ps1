# Populate long-term memory (RAG). Run from the repo root. (Mainly for Phase 2.)
# NOTE: your Docker image name depends on your folder name. Check with: docker images
param(
    [string]$ImageName = "philoagents-course-api"
)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
docker run --rm --network=philoagents-network --env-file philoagents-api/.env -v ./philoagents-api/data:/app/data $ImageName uv run python -m tools.create_long_term_memory
