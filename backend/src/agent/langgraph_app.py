# langgraph_app.py

from langgraph.graph import StateGraph
from agent.state import OSINTState

from agent.agents.query_parser_agent import query_parser_agent
from agent.agents.planner_agent import planner_agent
from agent.agents.retriever_pivot_agent import retriever_pivot_agent
from agent.agents.synthesis_agent import synthesis_agent
from agent.agents.judgement_agent import judgement_agent
from agent.agents.graph_builder_agent import graph_builder_agent
from agent.agents.deduplication_agent import deduplication_agent


# Agent node wrappers
def query_parser_node(state: OSINTState) -> dict:
    parsed = query_parser_agent(state.query)
    print("Parsed Data", parsed)
    return {"parsed": parsed}

def planner_node(state: OSINTState) -> dict:
    parsed = state.parsed
    tasks = planner_agent(
        parsed.get("entity_type", ""),
        parsed.get("entity_name", ""),
        parsed.get("keywords", ""),
        parsed.get("affiliation", ""),
        parsed.get("location", ""),
    )
    return {"tasks": tasks} if tasks else {}

def retriever_node(state: OSINTState) -> dict:
    parsed = state.parsed
    model_name = getattr(state, "retrieval_model", "gpt-4o-mini-search-preview")
    retrievals = retriever_pivot_agent(state.tasks, parsed["entity_name"], model_name)

    # Update provenance
    state.provenance = [
        {
            "task": task,
            "hash": v.get("hash"),
            "source": v.get("source"),
            "query_used": v.get("query_used"),
            "retrieved": v.get("retrieved"),
            "confidence": v.get("confidence"),
            "decayed_score": v.get("decayed_score"),
        }
        for task, v in retrievals.items()
    ]

    # Retry logic
    if state.retry_count is None:
        state.retry_count = 0
    state.retry_count += 1
    print(f"🔁 Retry attempt: {state.retry_count}")

    if not retrievals or all(float(r.get("confidence", 0)) < 0.5 for r in retrievals.values()):
        if state.retry_count >= 2:
            print("❌ Max retries reached.")
            return {"retrievals": {}}
        print("⚠️ Low-confidence retrievals – retrying...")
        return {"retrievals": None}

    return {"retrievals": retrievals} if retrievals else {}

def deduplication_node(state: OSINTState) -> dict:
    filtered = deduplication_agent(state.retrievals)
    print(f"🧼 Deduplication complete: {len(state.retrievals)} → {len(filtered)} items")
    return {"deduplicated": filtered} if filtered else {}

def synthesis_node(state: OSINTState) -> dict:
    parsed = state.parsed
    model_name = getattr(state, "synthesis_model", "gemini-1.5-pro")
    report = synthesis_agent(state.deduplicated, parsed["entity_name"], model_name)
    return {"report": report} if report else {}

def graph_node(state: OSINTState) -> dict:
    graph = graph_builder_agent(state.deduplicated)
    print(f"🕸 GraphBuilder created {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
    return {"graph": graph} if graph else {}

def judgement_node(state: OSINTState) -> dict:
    parsed = state.parsed
    judgement = judgement_agent(parsed["entity_name"], state.report, state.deduplicated)
    return {"judgement": judgement} if judgement else {}


# LangGraph builder
def build_graph():
    graph = StateGraph(OSINTState)

    # Register all nodes
    graph.add_node("QueryParser", query_parser_node)
    graph.add_node("Planner", planner_node)
    graph.add_node("Retriever", retriever_node)
    graph.add_node("Deduplicator", deduplication_node)
    graph.add_node("Synthesis", synthesis_node)
    graph.add_node("GraphBuilder", graph_node)
    graph.add_node("Judgement", judgement_node)

    # Set entry point
    graph.set_entry_point("QueryParser")

    # Conditional transition for Retriever
    def should_retry_retriever(state: dict) -> str:
        if not state.get("retrievals"):
            return "retry"
        return "success"

    graph.add_conditional_edges(
        "Retriever",
        should_retry_retriever,
        {
            "retry": "Retriever",
            "success": "Deduplicator"
        }
    )

    # Static edges
    graph.add_edge("QueryParser", "Planner")
    graph.add_edge("Planner", "Retriever")
    graph.add_edge("Deduplicator", "Synthesis")
    graph.add_edge("Synthesis", "GraphBuilder")
    graph.add_edge("GraphBuilder", "Judgement")

    # Set finish point
    graph.set_finish_point("Judgement")

    return graph.compile()
