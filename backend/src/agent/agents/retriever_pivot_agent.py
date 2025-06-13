import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict

import asyncio
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Scoring Functions ---

def estimate_confidence(content: str) -> float:
    if not content or "error" in content.lower():
        return 0.2
    elif "source" in content.lower() or "citation" in content.lower():
        return 0.9
    elif len(content) > 400:
        return 0.8
    elif len(content) > 200:
        return 0.6
    else:
        return 0.4

def compute_decay_score(published_date: str, base_confidence: float) -> float:
    try:
        days_old = (datetime.now() - datetime.strptime(published_date, "%Y-%m-%d")).days
    except Exception:
        days_old = 30
    decay_factor = 0.97 ** days_old
    return round(base_confidence * decay_factor, 3)

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# --- Async Web Search Task ---

async def run_web_search(task: str, entity_name: str, i: int, model_name: str) -> Dict:
    try:
        print(f"🔎 Running web search for task {i}: {task}")
        response = await client.chat.completions.create(
            model=model_name,
            web_search_options={},
            messages=[
                {
                    "role": "user",
                    "content": f"""
Limit the web search to 1–2 sources.
Task: {task} about {entity_name}. Provide a brief summary and cite sources.
"""
                }
            ]
        )

        message = response.choices[0].message
        content = message.content if isinstance(message.content, str) else str(message.content)

        urls = []
        if hasattr(message, "annotations"):
            for ann in message.annotations:
                if getattr(ann, "type", "") == "url_citation" and hasattr(ann, "url_citation") and len(urls) < 2:
                    citation = ann.url_citation
                    urls.append({
                        "url": citation.url,
                        "title": getattr(citation, "title", ""),
                        "start": getattr(citation, "start_index", None),
                        "end": getattr(citation, "end_index", None)
                    })

        base_conf = estimate_confidence(content)
        now = datetime.now()
        publish_date = now.strftime("%Y-%m-%d")
        decayed = compute_decay_score(publish_date, base_conf)

        return {
            f"task_{i}": {
                "source": "web_search_preview",
                "query_used": task,
                "published": publish_date,
                "retrieved": now.isoformat(),
                "data": content,
                "confidence": base_conf,
                "decayed_score": decayed,
                "hash": hash_text(content),
                "citations": urls
            }
        }

    except Exception as e:
        print(f"⚠️ Error in task {i}: {e}")
        return {
            f"task_{i}": {
                "source": "web_search_preview",
                "query_used": task,
                "retrieved": datetime.now().isoformat(),
                "confidence": 0.2,
                "decayed_score": compute_decay_score(datetime.now().strftime("%Y-%m-%d"), 0.2),
                "data": f"Error: {str(e)}",
                "hash": hash_text(str(e)),
                "citations": []
            }
        }

# --- Parallel Retriever Agent ---

def retriever_pivot_agent(tasks: List[str], entity_name: str, model_name: str = "gpt-4o-mini-search-preview") -> Dict[str, Dict]:
    async def gather_tasks():
        calls = [run_web_search(task, entity_name, i+1, model_name) for i, task in enumerate(tasks)]
        results = await asyncio.gather(*calls)
        merged = {}
        for r in results:
            merged.update(r)
        return merged

    return asyncio.run(gather_tasks())
