# PersianPoetAgents — Phase 1 Package 🎭

Goal of this phase: **the backend speaks Persian as 7 Persian poets** (سعدی، حافظ، مولوی، صائب، بیدل، اقبال، رهی معیری) through any OpenAI-compatible LLM API.

## What's inside (drop-in replacements)

| File in this zip | Replaces in your repo |
|---|---|
| `philoagents-api/src/philoagents/domain/philosopher_factory.py` | same path |
| `philoagents-api/src/philoagents/domain/prompts.py` | same path |
| `philoagents-api/src/philoagents/application/conversation_service/workflow/chains.py` | same path |
| `philoagents-api/src/philoagents/config.py` | same path |
| `philoagents-api/pyproject.toml` | same path (adds `langchain-openai`) |
| `philoagents-api/.env.example` | same path |
| `philoagents-api/data/extraction_metadata.json` | same path (used in Phase 2) |
| `scripts/*.ps1` | new folder — Windows helpers (no `make` needed) |

## ⚠️ Step 0 — BEFORE rebuilding: add the PyPI mirror

`pyproject.toml` changed (new dependency), so Docker **will re-run the dependency install layer**. To avoid another 75-minute download, open `philoagents-api/Dockerfile` and add these lines right after the `FROM ...` line (before any install/copy steps):

```dockerfile
ENV UV_INDEX_URL=https://mirror-pypi.runflare.com/simple/
ENV UV_HTTP_TIMEOUT=300
```

(Alternative mirror: `https://pypi.iranrepo.ir/simple`)

## Step 1 — Merge

1. Copy the files above into your repo at the same paths (overwrite).
2. Update `philoagents-api/.env`: add the new variables (see `.env.example`):
   - `LLM_API_KEY` — your OpenAI-compatible key (**required**)
   - `LLM_BASE_URL` — your provider's base URL, e.g. `https://api.openai.com/v1` or your gateway's URL
   - `LLM_MODEL` / `LLM_MODEL_SUMMARY` / `LLM_MODEL_CONTEXT_SUMMARY` — model names your provider serves
   - `GROQ_API_KEY` is now optional; you can leave it empty.

## Step 2 — Rebuild & run

```powershell
docker compose up --build -d
```

## Step 3 — Smoke test (Persian poet, no UI needed)

```powershell
# find your API image name first:
docker images

# then (use pwsh / PowerShell 7 for correct Persian text):
./scripts/call-agent.ps1 -PoetId hafez -ImageName <your-api-image-name>
```

Or open Swagger at `http://localhost:8000/docs` and POST to the chat endpoint with `philosopher_id: "hafez"` and a Persian message.

✅ **Success looks like:** a Persian reply, in character, introducing himself as حافظ.

## Known limitations (by design, coming in later phases)

- 🎮 **The game UI still shows the old philosopher NPCs** (Socrates etc.). Chatting with them in-game will fail because the backend no longer knows those IDs. UI remap = **Phase 3**. Test via `call-agent.ps1` or Swagger for now.
- 🧠 Long-term memory (RAG) still uses the English embedding model and hasn't been populated with Persian data. Do NOT run `create-long-term-memory` yet — that's **Phase 2** (Ganjoor + fa.wikipedia + multilingual embedder).
- 📊 Evaluation tooling still uses the original Groq/OpenAI wiring in places — **Phase 4**.
- The poets may occasionally quote verses from model memory. The prompt forbids invented verses, but the real fix (quote only retrieved Ganjoor verses + eval check) lands in **Phases 2 & 4**.

## Rollback

Everything is in git — `git checkout -- .` in the repo root undoes the merge.
