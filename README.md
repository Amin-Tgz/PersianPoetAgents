<div align="center">
  <h1>شاعران پارسی — PersianPoetAgents</h1>
  <p>An AI-powered game where you walk up to the great Persian poets and talk to them — in Persian, with real verses from their own divans.</p>
  <p>A fork of <a href="https://github.com/neural-maze/philoagents-course">PhiloAgents</a> (The Neural Maze &amp; Decoding ML), rebuilt for Persian poetry.</p>
</div>

---

## 🎭 About

PersianPoetAgents turns the PhiloAgents simulation engine into a Persian poetry experience. Instead of debating Plato and Aristotle, you wander a 2D town and converse — fully in Persian — with seven legendary Persian-language poets. Each poet is an agentic RAG system (LangGraph + MongoDB) whose long-term memory is populated with their **actual poems from [Ganjoor](https://ganjoor.net)** and their Persian Wikipedia biography, so when a poet quotes a بیت, it is a real one — retrieved, not hallucinated.

### The poets

| ID | Poet | Era | Corpus |
|----|------|-----|--------|
| `saadi` | سعدی | 13th c. | Ganjoor + fa.wikipedia |
| `hafez` | حافظ | 14th c. | Ganjoor + fa.wikipedia |
| `molavi` | مولوی (رومی) | 13th c. | Ganjoor + fa.wikipedia |
| `saeb` | صائب تبریزی | 17th c. | Ganjoor + fa.wikipedia |
| `bidel` | بیدل دهلوی | 17–18th c. | Ganjoor + fa.wikipedia |
| `iqbal` | اقبال لاهوری | 19–20th c. | Ganjoor + fa.wikipedia |
| `rahi` | رهی معیری | 20th c. | Ganjoor + fa.wikipedia |

## 🔀 What changed vs. the original course

**LLM — provider-agnostic (no Groq lock-in).** `chains.py` uses `ChatOpenAI` against any OpenAI-compatible gateway. Configure `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` in `.env` (tested with [AvalAI](https://avalai.ir); works with OpenAI, OpenRouter, Groq's OpenAI-compatible endpoint, LM Studio, etc.).

**Embeddings — multilingual, swappable.** Sentence-transformers were replaced with an OpenAI-compatible embeddings client (`EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`, `EMBEDDING_DIM`). Default setup: **BGE-M3 (1024-dim) served locally by LM Studio** on port 9966. Ingestion and querying must use the same model.

**Dataset — Ganjoor instead of Stanford Encyclopedia.** `tools/download_ganjoor.py` downloads each poet's poems from the Ganjoor API into `data/ganjoor/<poet_id>.json` (default 150 poems per poet). `extract.py` loads one document per poem (title + verses) plus the poet's Persian Wikipedia article fetched via the MediaWiki API.

**RAG tuned for poetry, not prose:**
- The retrieval tool is `retrieve_poet_verses`, and both its description and the character card force the model to call it before quoting any verse — poets may only quote lines that appear verbatim in retrieved chunks, and must not guess ghazal numbers.
- The upstream `summarize_context_node` (which compressed retrieved documents into a <50-word summary) was **removed from the graph** — it destroyed exact verses. Retrieved chunks now reach the poet verbatim.
- Dedup threshold raised from 0.7 to **0.9** (`RAG_DEDUP_THRESHOLD`): poems share meter/radif vocabulary without being duplicates; the upstream default deleted most of the corpus.

**Prompts — fully Persian.** Character cards, conversation summaries, context prompts, and the evaluation-dataset generator are all rewritten in Persian, with anti-hallucination rules (never invent a بیت; admit when a verse is not in the retrieved دیوان).

**UI — Persian and RTL.**
- 7 poet NPCs with Persian name labels (character sprites reused from the original game for now).
- Dialogue is a DOM overlay with a native RTL `<input>` — real Persian typing and correct letter shaping (the original drew text on the Phaser canvas, which breaks Persian).
- [Vazirmatn](https://github.com/rastikerdar/vazirmatn) font everywhere; Persian main menu, help, and pause menu.
- Replies stream over the original WebSocket API.

**Windows-friendly tooling.** All helper scripts are bash scripts designed for **Git Bash** on Windows (`MSYS_NO_PATHCONV=1` handled internally).

**Observability.** [Opik](https://www.comet.com/site/products/opik/) tracing/monitoring is kept from the original course (project: `persianpoetagents`).

## 🏗️ Project structure

```bash
.
├── philoagents-api/     # Backend: LangGraph agents, RAG, FastAPI + WebSocket (Python)
│   ├── data/ganjoor/    # Downloaded poem corpora (one JSON per poet)
│   ├── src/philoagents/ # Agent workflow, RAG, prompts, domain (poets)
│   └── tools/           # download_ganjoor.py, create_long_term_memory.py, call_agent.py …
├── philoagents-ui/      # Frontend: Phaser 3 game, Persian RTL UI (Node)
└── scripts/             # Git Bash helper scripts (download corpus, ingest, test agents)
```

(Directory names keep the original `philoagents-*` naming so upstream diffs stay easy to follow.)

## 🚀 Getting started

### Prerequisites

- Docker Desktop
- An API key for any OpenAI-compatible LLM provider (e.g. AvalAI / OpenAI / OpenRouter)
- [LM Studio](https://lmstudio.ai) running an embeddings server: load `text-embedding-bge-m3` and serve it on port **9966** (or point `EMBEDDING_BASE_URL` at any OpenAI-compatible embeddings endpoint)
- On Windows: Git Bash (comes with Git for Windows)

### 1. Configure `.env`

Create `philoagents-api/.env` (note: docker's env-file parser does **not** strip inline comments — keep values clean):

```env
# --- LLM (any OpenAI-compatible provider) ---
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.avalai.ir/v1
LLM_MODEL=gpt-5.4-mini
LLM_MODEL_SUMMARY=gpt-5.4-mini
LLM_MODEL_CONTEXT_SUMMARY=gpt-5.4-mini

# --- Embeddings (must match between ingestion and querying) ---
EMBEDDING_API_KEY=lm-studio
EMBEDDING_BASE_URL=http://host.docker.internal:9966/v1
EMBEDDING_MODEL=text-embedding-bge-m3
EMBEDDING_DIM=1024

# --- RAG ---
RAG_TOP_K=5
RAG_CHUNK_SIZE=256
RAG_DEDUP_THRESHOLD=0.9

# --- Opik (optional, for tracing/monitoring) ---
COMET_API_KEY=...
COMET_PROJECT=persianpoetagents
```

### 2. Start the stack

```bash
docker compose up -d --build     # MongoDB + API (port 8000) + UI (port 8080)
```

### 3. Build the poets' long-term memory (first run only)

```bash
# Download poems from Ganjoor (150 per poet by default)
bash scripts/download-ganjoor.sh

# Embed + ingest into MongoDB (requires the embeddings server to be running)
bash scripts/create-long-term-memory.sh
```

### 4. Test a poet from the terminal

```bash
bash scripts/call-agent.sh hafez "دیوان تو چه نام دارد؟ درباره غزل‌هایت برایم بگو."
```

### 5. Play

Open [http://localhost:8080](http://localhost:8080) — walk with the arrow keys, press **SPACE** near a poet to talk, type in Persian, **Enter** to send, **ESC** to close.

## 🛠️ Useful scripts (Git Bash)

| Script | What it does |
|--------|--------------|
| `scripts/download-ganjoor.sh [--poet ID] [--max-poems N]` | Download poem corpora from Ganjoor |
| `scripts/create-long-term-memory.sh` | Chunk, embed, dedup, and ingest corpora into MongoDB |
| `scripts/call-agent.sh <poet_id> "<question>"` | Ask a poet a question from the CLI |

## ⚠️ Known issues

- **Opik `token_usage` warnings** in logs (`TypeError: 'NoneType' …`): cosmetic. Some providers don't return token usage in streaming responses; traces still log fine.
- **Ghazal numbers can be wrong.** Poem titles are only prepended to the first chunk of each poem, so a poet may quote real verses but cite the wrong غزل number. Planned fix: prepend the title to every chunk at ingestion time.
- **Slow first token with reasoning models.** The model "thinks" and does a retrieval round trip before any text streams; non-reasoning models feel snappier.

## 🗺️ Roadmap

- **Evaluation:** regenerate the evaluation dataset in Persian (biography, works, famous verses, style) and add a verse-authenticity metric in Opik.
- **Corpus:** more poems per poet (especially صائب), poem titles on every chunk, poem/bio chunk tagging.
- **Deployment:** hosted BGE-M3 embeddings (DeepInfra / Cloudflare Workers AI), MongoDB Atlas M0, backend on a free cloud tier, UI on GitHub Pages.
- **Art:** custom sprites for each poet (currently reusing the original character atlases).

## 🙏 Credits

Built on the excellent open-source [PhiloAgents course](https://github.com/neural-maze/philoagents-course) by [The Neural Maze](https://theneuralmaze.substack.com) and [Decoding ML](https://decodingml.substack.com), in collaboration with MongoDB, Opik and Groq. Go take the course — it teaches everything this fork is built on.

Poetry data from [Ganjoor](https://ganjoor.net) (گنجور) and [Persian Wikipedia](https://fa.wikipedia.org). Persian font: [Vazirmatn](https://github.com/rastikerdar/vazirmatn) by Saber Rastikerdar.

## License

MIT — see [LICENSE](LICENSE). Same license as the original course.
