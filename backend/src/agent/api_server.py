# src/api_server.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import uuid
import json
import time

from agent.chat_logger import log_session, log_message, get_chat_history, init_db
from agent.langgraph_app import build_graph
from agent.state import OSINTState
from agent.audit_log import save_osint_state_to_file, load_osint_state_from_file

app = FastAPI()

# ✅ Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
graph = build_graph()

# ================================
# REQUEST MODELS
# ================================

class ChatRequest(BaseModel):
    session_id: str
    entity_name: str
    user_message: str

class InvestigationRequest(BaseModel):
    query: str
    retrieval_model: Optional[str] = "gpt-4o-mini-search-preview"
    synthesis_model: Optional[str] = "gemini-2.0-flash"

# ================================
# OSINT Investigation (Basic)
# ================================

@app.post("/osint/investigate")
def investigate(payload: InvestigationRequest):
    session_id = str(uuid.uuid4())
    state = {
        "query": payload.query,
        "retrieval_model": payload.retrieval_model,
        "synthesis_model": payload.synthesis_model
    }

    final_state = graph.invoke(state)
    save_osint_state_to_file(final_state, final_state["parsed"]["entity_name"])

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

# ================================
# OSINT Streaming Response
# ================================

@app.post("/osint/investigate-stream")
def investigate_stream(payload: InvestigationRequest):
    session_id = str(uuid.uuid4())
    state = {
        "query": payload.query,
        "retrieval_model": payload.retrieval_model,
        "synthesis_model": payload.synthesis_model,
    }

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

# ================================
# Chat History API (existing)
# ================================

@app.get("/chat/{session_id}")
def get_history(session_id: str):
    return get_chat_history(session_id)

# ================================
# ✅ NEW: Audit Log Endpoints
# ================================

AUDIT_LOG_DIR = Path("output_logs")

@app.get("/osint/history")
def list_investigation_logs():
    files = sorted(AUDIT_LOG_DIR.glob("*.json"), reverse=True)
    return [f.name for f in files]

@app.get("/osint/history/view/{filename}")
def get_log_file(filename: str):
    file_path = AUDIT_LOG_DIR / filename
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(file_path)

@app.get("/osint/history/load/{filename}")
def load_osint_state(filename: str):
    file_path = AUDIT_LOG_DIR / filename
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    osint_state = load_osint_state_from_file(str(file_path))
    return osint_state.dict()
