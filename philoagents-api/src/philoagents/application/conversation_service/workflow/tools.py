from langchain.tools.retriever import create_retriever_tool

from philoagents.application.rag.retrievers import get_retriever
from philoagents.config import settings

retriever = get_retriever(
    embedding_model_id=settings.RAG_TEXT_EMBEDDING_MODEL_ID,
    k=settings.RAG_TOP_K,
    device=settings.RAG_DEVICE,
)

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_poet_verses",
    (
        "Search the poet's authentic poems and biographical documents "
        "(Persian Ganjoor corpus). "
        "ALWAYS call this tool BEFORE quoting any verse, beyt, ghazal, or poem, "
        "and whenever the user asks about the poet's poetry, works, books, life, "
        "style, or ideas - even if you think you already know the answer. "
        "Never quote poetry from memory: verses not returned by this tool must "
        "not be quoted. "
        "Query with a Persian phrase combining the poet's name and the topic, "
        "e.g. '\u0635\u0627\u0626\u0628 \u062a\u0628\u0631\u06cc\u0632\u06cc \u0628\u06cc\u062a \u062f\u0631\u0628\u0627\u0631\u0647 \u0639\u0634\u0642'."
    ),
)

tools = [retriever_tool]
