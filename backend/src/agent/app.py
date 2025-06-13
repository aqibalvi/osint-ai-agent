# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import fastapi.exceptions

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define the FastAPI app
app = FastAPI()


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir
    static_files_path = build_path / "assets"  # Vite uses 'assets' subdir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    build_dir = pathlib.Path(build_dir)

    react = FastAPI(openapi_url="")
    react.mount(
        "/assets", StaticFiles(directory=static_files_path), name="static_assets"
    )

    @react.get("/{path:path}")
    async def handle_catch_all(request: Request, path: str):
        fp = build_path / path
        if not fp.exists() or not fp.is_file():
            fp = build_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    return react


# from agent.agents.query_parser_agent import query_parser_agent
# from agent.agents.planner_agent import planner_agent
# from agent.agents.retriever_pivot_agent import retriever_pivot_agent
# from agent.agents.synthesis_agent import synthesis_agent
# from agent.agents.judgement_agent import judgement_agent

# if __name__ == "__main__":

#     # STEP 1: Parse the user query
#     query = "Investigate Muhammad Aqib Iqbal who works in Turing, a Pakistani who lives in Oman"
#     print("\n🔍 Parsing Query...")
#     parsed = query_parser_agent(query)
#     # print("✅ Parsed:", parsed)

#     # STEP 2: Generate investigation tasks
#     print("\n🧠 Planning Tasks...")
#     tasks = planner_agent(parsed["entity_type"], parsed["entity_name"], parsed["keywords"], parsed["affiliation"])
#     # print("✅ Planner Agent Tasks:")
#     # for task in tasks:
#     #     print(" -", task)

#     # STEP 3: Retrieve data via web search
#     print("\n🌐 Running Real-Time Web Search...")
#     retrievals = retriever_pivot_agent(tasks, parsed["entity_name"])
#     # for k, v in retrievals.items():
#     #     print(f"\n🔹 Task: {k}\n   Source: {v['source']}\n   Confidence: {v['confidence']}\n   Data: {v['data'][:300]}...")


#     # STEP 4: Synthesize intelligence report
#     print("\n🧾 Synthesizing OSINT Report...")
#     report = synthesis_agent(retrievals, parsed["entity_name"])
#     print("\n✅ Final OSINT Intelligence Report:\n")
#     print(report)

#     judgement = judgement_agent(parsed["entity_name"], report, retrievals)


#     # STEP 5: Final QA by Claude Opus 4
#     print("✅ Final QA by Claude Opus 4:")
#     print(f"Credibility Score: {judgement['credibility_score']}")
#     print("Flagged Issues:")
#     for issue in judgement['flagged_issues']:
#         print(f" - {issue}")
#     print("\n📝 Final Revised Report:\n")
#     print(judgement["revised_report"])

# src/app.py

from langgraph_app import build_graph
from audit_log import save_osint_state_to_file
from chat_logger import init_db, log_session, log_message, get_chat_history

if __name__ == "__main__":
    init_db()

    # Replace with real session from frontend later
    session_id = "session_cli_001"
    input_query = "Investigate Ali Khaledi Nasab an Irani AI Researcher working for Amazon"

    graph = build_graph()
    final_state = graph.invoke({
    "query": input_query,
    "retrieval_model": "gpt-4o-mini-search-preview",  # or "gpt-4o"
    "synthesis_model": "gemini-2.0-flash"              # or "gemini-2.0-flash"
})

    log_session(session_id, entity=final_state["parsed"]["entity_name"])
    log_message(session_id, "user", input_query)

    log_message(session_id, "assistant", final_state["report"])

    print("\n✅ Final Report:\n")
    print(final_state["report"])

    print("\n🧠 Credibility Score:", final_state["judgement"].get("credibility_score", "N/A"))
    print("🚩 Issues flagged:")
    for issue in final_state["judgement"].get("flagged_issues", []):
        print(f" - {issue}")

    print("\n🕸 Graph Summary:")
    print("Nodes:", len(final_state["graph"].get("nodes", [])))
    print("Edges:", len(final_state["graph"].get("edges", [])))

    save_osint_state_to_file(final_state, final_state["parsed"]["entity_name"])


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
