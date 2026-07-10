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
    # NOTE (Phase 2): this English-focused model will be replaced by a
    # configurable multilingual embedder (API or local BGE-M3 / multilingual-e5).
    RAG_TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_TEXT_EMBEDDING_MODEL_DIM: int = 384
    RAG_TOP_K: int = 3
    RAG_DEVICE: str = "cpu"
    RAG_CHUNK_SIZE: int = 256

    # --- Paths Configuration ---
    EVALUATION_DATASET_FILE_PATH: Path = Path("data/evaluation_dataset.json")
    EXTRACTION_METADATA_FILE_PATH: Path = Path("data/extraction_metadata.json")


settings = Settings()
