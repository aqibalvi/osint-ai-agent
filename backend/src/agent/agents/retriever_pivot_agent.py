#backend/src/agent/agents/retriever_pivot_agent.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from datetime import datetime
import hashlib
from typing import List, Dict
from openai import OpenAI

client = OpenAI()  

# Confidence scoring logic based on heuristics
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

# Hashing for provenance
def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# Time-decay scoring
def compute_decay_score(published_date: str, base_confidence: float) -> float:
    try:
        days_old = (datetime.now() - datetime.strptime(published_date, "%Y-%m-%d")).days
    except Exception:
        days_old = 30  # fallback if publish date is unknown
    decay_factor = 0.97 ** days_old
    return round(base_confidence * decay_factor, 3)

# Main retriever agent
def retriever_pivot_agent(tasks: List[str], entity_name: str, model_name: str = "gpt-4o-mini-search-preview") -> Dict[str, Dict]:

    results = {}

    for i, task in enumerate(tasks, start=1):
        try:
            print(f"🔎 Running web search for task {i}: {task}")
            response = client.chat.completions.create(
                model=model_name,
                web_search_options={},
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Limit the web search to first 1–2 sources only.
                        Task: {task} about {entity_name}. Provide a brief summary and cite 1–2 sources if possible.
                        """
                    }
                ]
            )

            message = response.choices[0].message
            content = message.content if isinstance(message.content, str) else str(message.content)

            # ✅ Use dot notation here
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
            # print("📎 Extracted citations:")
            # for c in urls:
            #     print(f" - {c['title']}: {c['url']}")

            base_confidence = estimate_confidence(content)

            # Timestamp now (assume publish date unknown)
            now = datetime.now()
            publish_date = now.strftime("%Y-%m-%d")
            decayed_score = compute_decay_score(publish_date, base_confidence)

            results[f"task_{i}"] = {
                "source": "web_search_preview",
                "query_used": task,
                "published": publish_date,
                "retrieved": now.isoformat(),
                "data": content,
                "confidence": base_confidence,
                "decayed_score": decayed_score,
                "hash": hash_text(content),
                "citations": urls
            }

        except Exception as e:
            print(f"⚠️ Error in task {i}: {e}")
            results[f"task_{i}"] = {
                "source": "web_search_preview",
                "query_used": task,
                "retrieved": datetime.now().isoformat(),
                "confidence": 0.2,
                "decayed_score": compute_decay_score(datetime.now().strftime("%Y-%m-%d"), 0.2),
                "data": f"Error retrieving result: {str(e)}",
                "hash": hash_text(str(e)),
                "citations": []
            }

    return results