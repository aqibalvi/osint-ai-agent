# src/api_server.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi.responses import StreamingResponse
import json
import time

from agent.chat_logger import log_session, log_message, get_chat_history, init_db
from agent.langgraph_app import build_graph
from typing import Optional

from agent.state import OSINTState
from agent.audit_log import save_osint_state_to_file
import uuid



app = FastAPI()

# ✅ Allow frontend on localhost:5173 to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
graph = build_graph()

class ChatRequest(BaseModel):
    session_id: str
    entity_name: str
    user_message: str



class InvestigationRequest(BaseModel):
    query: str
    retrieval_model: Optional[str] = "gpt-4o-mini-search-preview"
    synthesis_model: Optional[str] = "gemini-1.5-pro"

@app.post("/osint/investigate")
def investigate(payload: InvestigationRequest):
    session_id = str(uuid.uuid4())

    # Convert OSINTState to dict for LangGraph
    state = {
        "query": payload.query,
        "retrieval_model": payload.retrieval_model,
        "synthesis_model": payload.synthesis_model
    }

    graph = build_graph()
    final_state = graph.invoke(state)

    # Save results for audit/debugging
    save_osint_state_to_file(final_state, final_state["parsed"]["entity_name"])

    # ✅ Deduplicate citations (by URL + title)
    seen = set()
    citation_urls = []
    for task in final_state["retrievals"].values():
        for c in task.get("citations", []):
            url = c.get("url", "").strip().lower().rstrip("/")
            title = c.get("title", "").strip()
            key = (url, title)
            if url and key not in seen:
                seen.add(key)
                citation_urls.append({"url": url, "title": title})

    return {
        "session_id": session_id,
        "entity": final_state["parsed"]["entity_name"],
        "report": final_state["report"],
        "graph": final_state["graph"],
        "judgement": final_state["judgement"],
        "retrievals": final_state["retrievals"],
        "citations": citation_urls,
        "flagged_issues": final_state["judgement"].get("flagged_issues", []),
        "credibility_score": final_state["judgement"].get("credibility_score"),
    }

@app.post("/osint/investigate-stream")
def investigate_stream(payload: InvestigationRequest):
    session_id = str(uuid.uuid4())
    state = {
        "query": payload.query,
        "retrieval_model": payload.retrieval_model,
        "synthesis_model": payload.synthesis_model,
    }
    graph = build_graph()

    def generate():
        yield json.dumps({"step": "Analyzing Query 🔍"}) + "\n"
        time.sleep(0.5)
        yield json.dumps({"parsed": state["query"]}) + "\n"

        yield json.dumps({"step": "Planning OSINT Tasks 🧠"}) + "\n"
        time.sleep(0.5)

        yield json.dumps({"step": "Running Web Searches 🌐"}) + "\n"
        for i in range(1, 9):
            yield json.dumps({"search": f"🔎 Running web search for task {i}..."}) + "\n"
            time.sleep(0.3)

        yield json.dumps({"step": "Scoring & Evaluating Sources 📊"}) + "\n"
        time.sleep(1)

        yield json.dumps({"step": "Synthesizing Final Report 📝"}) + "\n"
        final_state = graph.invoke(state)
        save_osint_state_to_file(final_state, final_state["parsed"]["entity_name"])

        # ✅ Deduplicate citations (by URL + title)
        seen = set()
        citation_urls = []
        for task in final_state["retrievals"].values():
            for c in task.get("citations", []):
                url = c.get("url", "").strip().lower().rstrip("/")
                title = c.get("title", "").strip()
                key = (url, title)
                if url and key not in seen:
                    seen.add(key)
                    citation_urls.append({"url": url, "title": title})

        yield json.dumps({
            "final": {
                "report": final_state["report"],
                "credibility_score": final_state["judgement"]["credibility_score"],
                "flagged_issues": final_state["judgement"]["flagged_issues"],
                "parsed": final_state["parsed"],
                "citations": citation_urls
            }
        }) + "\n"

    return StreamingResponse(generate(), media_type="text/event-stream")



@app.get("/chat/{session_id}")
def get_history(session_id: str):
    return get_chat_history(session_id)
