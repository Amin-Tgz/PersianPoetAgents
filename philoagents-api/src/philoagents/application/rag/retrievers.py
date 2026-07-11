from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers import (
    MongoDBAtlasHybridSearchRetriever,
)
from loguru import logger

from philoagents.config import settings

from .embeddings import EmbeddingsModel, get_embedding_model

Retriever = MongoDBAtlasHybridSearchRetriever


def get_retriever(
    embedding_model_id: str | None = None,
    k: int = 3,
    device: str = "cpu",
) -> Retriever:
    """Creates and returns a hybrid search retriever with the specified embedding model.

    Args:
        embedding_model_id (str | None): The identifier for the embedding model to use.
            Defaults to settings.EMBEDDING_MODEL.
        k (int, optional): Number of documents to retrieve. Defaults to 3.
        device (str, optional): Kept for backwards compatibility. Unused with
            API embeddings.

    Returns:
        Retriever: A configured hybrid search retriever.
    """
    model_id = embedding_model_id or settings.EMBEDDING_MODEL
    logger.info(
        f"Initializing retriever | model: {model_id} | base_url: {settings.EMBEDDING_BASE_URL} | top_k: {k}"
    )

    embedding_model = get_embedding_model(model_id, device)

    return get_hybrid_search_retriever(embedding_model, k)


def get_hybrid_search_retriever(
    embedding_model: EmbeddingsModel, k: int
) -> MongoDBAtlasHybridSearchRetriever:
    """Creates a MongoDB Atlas hybrid search retriever with the given embedding model.

    Args:
        embedding_model (EmbeddingsModel): The embedding model to use for vector search.
        k (int): Number of documents to retrieve.

    Returns:
        MongoDBAtlasHybridSearchRetriever: A configured hybrid search retriever using both
        vector and text search capabilities.
    """
    vectorstore = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=settings.MONGO_URI,
        embedding=embedding_model,
        namespace=f"{settings.MONGO_DB_NAME}.{settings.MONGO_LONG_TERM_MEMORY_COLLECTION}",
        text_key="chunk",
        embedding_key="embedding",
        relevance_score_fn="dotProduct",
    )

    retriever = MongoDBAtlasHybridSearchRetriever(
        vectorstore=vectorstore,
        search_index_name="hybrid_search_index",
        top_k=k,
        vector_penalty=50,
        fulltext_penalty=50,
    )

    return retriever
