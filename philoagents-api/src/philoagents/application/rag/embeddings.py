from langchain_openai import OpenAIEmbeddings

from philoagents.config import settings

EmbeddingsModel = OpenAIEmbeddings


def get_embedding_model(
    model_id: str | None = None,
    device: str = "cpu",
) -> EmbeddingsModel:
    """Gets an embedding model served over any OpenAI-compatible API.

    The provider is controlled by EMBEDDING_BASE_URL + EMBEDDING_API_KEY in
    .env, so the same code works with LM Studio (local BGE-M3), DeepInfra,
    Cloudflare Workers AI, AvalAI, or any other OpenAI-compatible endpoint.

    Args:
        model_id: The embedding model id exposed by the provider. Defaults to
            settings.EMBEDDING_MODEL.
        device: Kept for backwards compatibility with the original local
            (HuggingFace) implementation. Unused with API embeddings.

    Returns:
        EmbeddingsModel: A configured OpenAI-compatible embeddings client.
    """
    return OpenAIEmbeddings(
        api_key=settings.EMBEDDING_API_KEY,
        base_url=settings.EMBEDDING_BASE_URL,
        model=model_id or settings.EMBEDDING_MODEL,
        # Send raw strings instead of tiktoken token arrays. Required for
        # non-OpenAI backends such as LM Studio, DeepInfra, AvalAI, etc.
        check_embedding_ctx_length=False,
        # Small batches: the default is 1000 texts per request, which makes a
        # local LM Studio server grind for minutes on one request with zero
        # console output (it looks like a hang).
        chunk_size=32,
        # Show a tqdm progress bar per embedding batch so ingestion progress
        # is visible in the console.
        show_progress_bar=True,
        # Fail fast instead of silently retrying for ~10 minutes when the
        # embedding server is unreachable.
        timeout=120,
        max_retries=1,
    )
