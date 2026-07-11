# Phase 2 — Persian RAG (long-term memory)

This package gives the poets real memory: Persian Wikipedia biographies +
real poems from Ganjoor (گنجور), embedded with BGE-M3 served by LM Studio
over the OpenAI protocol.

## What changed

| File | Change |
|---|---|
| `src/philoagents/application/rag/embeddings.py` | HuggingFace local model → OpenAI-compatible embeddings client (`EMBEDDING_*` in `.env`) |
| `src/philoagents/application/rag/retrievers.py` | Updated for the new embeddings client (same hybrid MongoDB retriever) |
| `src/philoagents/application/data/extract.py` | Wikipedia now `lang="fa"` (exact title from metadata URLs); Stanford Encyclopedia replaced by Ganjoor corpus loader |
| `src/philoagents/config.py` | New `EMBEDDING_*` + `GANJOOR_*` settings; legacy `RAG_TEXT_EMBEDDING_MODEL_ID/DIM` now alias to them |
| `tools/download_ganjoor.py` | NEW — downloads poems per poet from api.ganjoor.net into `data/ganjoor/<poet_id>.json` |
| `.env.example` | New `EMBEDDING_*` variables |
| `scripts/*.ps1` | Windows helpers with source mounts (no rebuild needed for these changes!) |

**NOT changed:** `pyproject.toml` / `uv.lock` — `langchain-openai` (added in Phase 1)
already covers the embeddings client, so **no Docker rebuild is required**.
Dropping torch/sentence-transformers to slim the image is deferred to Phase 5.

## Setup order

1. **Merge** these files into your repo (overwrite existing ones).
2. **Update `philoagents-api/.env`** — add the `EMBEDDING_*` block from
   `.env.example`. Set the port to your LM Studio server (e.g. 9966) and the
   exact model id from `GET /v1/models`. No inline comments!
3. **LM Studio**: load `bge-m3`, start the server, and enable serving on the
   local network (the container connects via `host.docker.internal`).
4. **Download poems** (~10-20 min for all 7 poets, cached in `data/ganjoor/`):
   ```powershell
   ./scripts/download-ganjoor.ps1
   ```
   Options: `./scripts/download-ganjoor.ps1 --poet hafez --max-poems 50`
5. **Build the memory** (extracts, chunks, embeds, recreates the 1024-dim index):
   ```powershell
   ./scripts/create-long-term-memory.ps1
   ```
6. **Test factual recall**:
   ```powershell
   ./scripts/call-agent.ps1 -PoetId hafez -Query "دیوان تو چه بخش‌هایی دارد؟ یک بیت مشهور خودت را بخوان."
   ```

## Notes & gotchas

- **Same model everywhere**: vectors written at ingestion must come from the
  same embedding model used at query time. If you switch providers/models
  later (e.g. AvalAI `text-embedding-3-small`, DIM 1536), update `.env` and
  re-run step 5 once.
- **Old memory is wiped** on each run of step 5 (by design, avoids duplicates
  and stale 384-dim vectors from the original course data).
- **iqbal**: Ganjoor hosts اقبال لاهوری's Persian works, which is what we want
  (Urdu corpus excluded by design).
- **Ganjoor API shape**: if the API returns errors on category/poem endpoints,
  run with `--poet hafez --max-poems 5` first and paste the log output —
  endpoint fallbacks are built in, but the API may evolve.
- The in-game NPCs still 404 until Phase 3 (UI remap) — keep testing via
  `call-agent.ps1` or Swagger at `localhost:8000/docs`.
