from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from philoagents.application.conversation_service.workflow.tools import tools
from philoagents.config import settings
from philoagents.domain.prompts import (
    CONTEXT_SUMMARY_PROMPT,
    EXTEND_SUMMARY_PROMPT,
    PHILOSOPHER_CHARACTER_CARD,
    SUMMARY_PROMPT,
)


def get_chat_model(
    temperature: float = 0.7, model_name: str | None = None
) -> ChatOpenAI:
    """Returns a chat model backed by any OpenAI-compatible API.

    The provider is fully controlled by LLM_BASE_URL + LLM_API_KEY in .env,
    so the same code works with OpenAI, OpenRouter, Groq's OpenAI-compatible
    endpoint, or any other OpenAI-compatible gateway.
    """
    return ChatOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model=model_name or settings.LLM_MODEL,
        temperature=temperature,
        # Ask the provider to include token usage in streaming responses so
        # Opik can log cost/usage per trace (harmless if unsupported).
        stream_usage=True,
    )


def get_philosopher_response_chain():
    model = get_chat_model()
    model = model.bind_tools(tools)
    system_message = PHILOSOPHER_CHARACTER_CARD

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message.prompt),
            MessagesPlaceholder(variable_name="messages"),
        ],
        template_format="jinja2",
    )

    return prompt | model


def get_conversation_summary_chain(summary: str = ""):
    model = get_chat_model(model_name=settings.LLM_MODEL_SUMMARY)

    summary_message = EXTEND_SUMMARY_PROMPT if summary else SUMMARY_PROMPT

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            ("human", summary_message.prompt),
        ],
        template_format="jinja2",
    )

    return prompt | model


def get_context_summary_chain():
    model = get_chat_model(model_name=settings.LLM_MODEL_CONTEXT_SUMMARY)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", CONTEXT_SUMMARY_PROMPT.prompt),
        ],
        template_format="jinja2",
    )

    return prompt | model
