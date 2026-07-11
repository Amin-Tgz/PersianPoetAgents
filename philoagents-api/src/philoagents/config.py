from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )

    # --- LLM (OpenAI-compatible) Configuration ---
    # Works with OpenAI, OpenRouter, Groq's OpenAI-compatible endpoint,
    # or any other OpenAI-compatible gateway. Set these in .env.
    LLM_API_KEY: str
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MODEL_SUMMARY: str = "gpt-4o-mini"
    LLM_MODEL_CONTEXT_SUMMARY: str = "gpt-4o-mini"

    # --- Embeddings (OpenAI-compatible) Configuration ---
    # Works with LM Studio (local BGE-M3), DeepInfra, Cloudflare Workers AI,
    # AvalAI, or any other OpenAI-compatible embeddings endpoint.
    # IMPORTANT: ingestion and querying must use the SAME model, and
    # EMBEDDING_DIM must match the model's output size (BGE-M3 = 1024).
    EMBEDDING_API_KEY: str = "lm-studio"
    EMBEDDING_BASE_URL: str = "http://host.docker.internal:1234/v1"
    EMBEDDING_MODEL: str = "text-embedding-bge-m3"
    EMBEDDING_DIM: int = 1024

    # --- Legacy Groq/OpenAI Configuration (kept optional for course tooling) ---
    GROQ_API_KEY: str | None = None
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_LLM_MODEL_SUMMARY: str = "llama-3.1-8b-instant"
    GROQ_LLM_MODEL_CONTEXT_SUMMARY: str = "llama-3.1-8b-instant"

    # --- OpenAI Configuration (only used by the original evaluation tooling) ---
    OPENAI_API_KEY: str | None = None

    # --- MongoDB Configuration ---
    MONGO_URI: str = Field(
        default="mongodb://philoagents:philoagents@local_dev_atlas:27017/?directConnection=true",
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    MONGO_DB_NAME: str = "philoagents"
    MONGO_STATE_CHECKPOINT_COLLECTION: str = "philosopher_state_checkpoints"
    MONGO_STATE_WRITES_COLLECTION: str = "philosopher_state_writes"
    MONGO_LONG_TERM_MEMORY_COLLECTION: str = "philosopher_long_term_memory"

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="persianpoetagents",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Agents Configuration ---
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 30
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5

    # --- RAG Configuration ---
    RAG_TOP_K: int = 5
    RAG_DEVICE: str = "cpu"  # kept for compatibility; unused with API embeddings
    RAG_CHUNK_SIZE: int = 256
    # Similarity threshold above which two chunks are considered duplicates.
    # Poetry shares many words (radif, refrains, meter vocabulary) without
    # being duplicated, so keep this high: only near-verbatim chunks are
    # removed. The upstream default of 0.7 removed most of the poem corpus.
    RAG_DEDUP_THRESHOLD: float = 0.9

    # --- Ganjoor Configuration ---
    GANJOOR_API_BASE: str = "https://api.ganjoor.net"
    GANJOOR_DATA_DIR: Path = Path("data/ganjoor")
    GANJOOR_MAX_POEMS_PER_POET: int = 150

    # --- Paths Configuration ---
    EVALUATION_DATASET_FILE_PATH: Path = Path("data/evaluation_dataset.json")
    EXTRACTION_METADATA_FILE_PATH: Path = Path("data/extraction_metadata.json")

    # Legacy aliases used across the original codebase; they now resolve to
    # the EMBEDDING_* settings above so untouched files keep working.
    @property
    def RAG_TEXT_EMBEDDING_MODEL_ID(self) -> str:
        return self.EMBEDDING_MODEL

    @property
    def RAG_TEXT_EMBEDDING_MODEL_DIM(self) -> int:
        return self.EMBEDDING_DIM


settings = Settings()
