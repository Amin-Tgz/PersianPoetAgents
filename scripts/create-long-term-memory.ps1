param(
    [string]$ImageName = "persianpoetagents-api:latest"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Builds the poets' long-term memory: extracts fa.wikipedia + Ganjoor corpora,
# chunks, embeds via EMBEDDING_BASE_URL, and (re)creates the MongoDB hybrid
# index with EMBEDDING_DIM dimensions. Requires: infrastructure up (MongoDB),
# LM Studio server running, and data/ganjoor/ populated by download-ganjoor.ps1.
docker run --rm -e UV_INDEX_URL=https://pypi.org/simple --network=philoagents-network --env-file philoagents-api/.env -v ./philoagents-api/data:/app/data -v ./philoagents-api/src/philoagents:/app/philoagents -v ./philoagents-api/tools:/app/tools $ImageName uv run python -m tools.create_long_term_memory
