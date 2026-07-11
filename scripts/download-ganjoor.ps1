param(
    [string[]]$Poet = @(),
    [int]$MaxPoems = 0,
    [string]$ImageName = "persianpoetagents-api:latest"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Downloads poem corpora from api.ganjoor.net into philoagents-api/data/ganjoor/.
# Source + tools are mounted so no image rebuild is needed for code changes.
# Usage examples:
#   ./scripts/download-ganjoor.ps1                          # all 7 poets, default limit
#   ./scripts/download-ganjoor.ps1 -Poet hafez -MaxPoems 5  # quick smoke test
#   ./scripts/download-ganjoor.ps1 -Poet hafez,saadi        # a subset of poets

$extraArgs = @()
foreach ($p in $Poet) { $extraArgs += @("--poet", $p) }
if ($MaxPoems -gt 0) { $extraArgs += @("--max-poems", "$MaxPoems") }

docker run --rm -e UV_INDEX_URL=https://pypi.org/simple --env-file philoagents-api/.env -v ./philoagents-api/data:/app/data -v ./philoagents-api/src/philoagents:/app/philoagents -v ./philoagents-api/tools:/app/tools $ImageName uv run python -m tools.download_ganjoor @extraArgs
