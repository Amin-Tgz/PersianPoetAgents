from functools import lru_cache

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from philoagents.application.conversation_service.workflow.edges import (
    should_summarize_conversation,
)
from philoagents.application.conversation_service.workflow.nodes import (
    conversation_node,
    summarize_conversation_node,
    retriever_node,
    connector_node,
)
from philoagents.application.conversation_service.workflow.state import PhilosopherState


@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(PhilosopherState)

    # Add all nodes
    graph_builder.add_node("conversation_node", conversation_node)
    graph_builder.add_node("retrieve_philosopher_context", retriever_node)
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)
    graph_builder.add_node("connector_node", connector_node)

    # Define the flow
    graph_builder.add_edge(START, "conversation_node")
    graph_builder.add_conditional_edges(
        "conversation_node",
        tools_condition,
        {
            "tools": "retrieve_philosopher_context",
            END: "connector_node",
        },
    )
    # NOTE (PersianPoetAgents): the original course routed retrieved documents
    # through summarize_context_node, which compressed them into a <50-word
    # prose summary before the model saw them. That destroys exact verses,
    # which is fatal for a poetry agent. Retrieved chunks now reach the
    # conversation node verbatim so poets can quote real lines word-for-word.
    graph_builder.add_edge("retrieve_philosopher_context", "conversation_node")
    graph_builder.add_conditional_edges("connector_node", should_summarize_conversation)
    graph_builder.add_edge("summarize_conversation_node", END)

    return graph_builder


# Compiled without a checkpointer. Used for LangGraph Studio
graph = create_workflow_graph().compile()
