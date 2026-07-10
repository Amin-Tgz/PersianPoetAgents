# Smoke-test a poet directly (bypasses the UI). Run from the repo root.
# NOTE: your Docker image name depends on your folder name. Check with: docker images
# Use PowerShell 7+ (pwsh) so the Persian text is passed correctly.
param(
    [string]$PoetId = "hafez",
    [string]$Query = "سلام! خودت را معرفی کن.",
    [string]$ImageName = "philoagents-course-api"
)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
docker run --rm -e UV_INDEX_URL=https://pypi.org/simple --network=philoagents-network --env-file philoagents-api/.env -v ./philoagents-api/data:/app/data $ImageName uv run python -m tools.call_agent --philosopher-id "$PoetId" --query "$Query"
