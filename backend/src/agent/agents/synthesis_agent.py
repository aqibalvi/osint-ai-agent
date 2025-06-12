import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from collections import defaultdict

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def synthesis_agent(retrievals: dict, entity_name: str, model_name: str = "gemini-1.5-pro") -> str:
    model = genai.GenerativeModel(model_name)
    today = datetime.now().strftime("%B %d, %Y")

    # Extract and sort retrievals by decayed score (descending)
    scored = [
        {
            "task": k,
            "summary": v.get("data", "")[:600],
            "source": v.get("source"),
            "confidence": v.get("confidence"),
            "decayed_score": v.get("decayed_score"),
            "published": v.get("published"),
            "retrieved": v.get("retrieved"),
            "hash": v.get("hash"),
            "query_used": v.get("query_used"),
            "citations": v.get("citations", [])
        }
        for k, v in retrievals.items()
    ]
    top_results = sorted(scored, key=lambda x: x["decayed_score"], reverse=True)[:10]

    # Create "Sources Used" block
    source_summaries = "\n".join([
        f"🔹 **{r['task']}** | Confidence: {r['confidence']:.2f}, Decayed Score: {r['decayed_score']:.2f}\n"
        f"Published: {r['published']} | Retrieved: {r['retrieved']} | Source: {r['source']} | Query: {r['query_used']}\n"
        f"Hash: `{r['hash']}`\n"
        f"Summary: {r['summary']}\n"
        for r in top_results
    ])

    # Deduplicated global citation list
    citation_set = set()
    for r in top_results:
        for c in r.get("citations", []):
            citation_set.add((c["url"], c.get("title", "")))

    citation_list = list(citation_set)
    citation_section = "\n".join([
        f"[{title or 'External Source'}]({url})" for url, title in citation_list
    ]) if citation_list else "No URLs were available from the search API for citation."

    # Deduplicated task-wise URLs (max 2 per task)
    seen_urls = set()
    task_urls = defaultdict(list)
    for r in top_results:
        task = r["task"]
        added = 0
        for c in r.get("citations", []):
            url = c["url"]
            if url not in seen_urls and added < 2:
                seen_urls.add(url)
                task_urls[task].append(url)
                added += 1

    per_task_sources = "\n".join([
        f"🔹 **{task}**:\n" + "\n".join([f"- {url}" for url in urls])
        for task, urls in task_urls.items()
    ]) if task_urls else "No task-level URLs available."

    # Final prompt
    prompt = f"""
You are an elite OSINT synthesis agent.

Use only the curated summaries and citations below to write an intelligence report on **{entity_name}**. Do not fabricate or speculate. Only base your report on what’s provided.

Each task below includes:
- A short summary
- Confidence & decay scores
- Timestamps
- Citations (if any)

---

## OSINT Intelligence Report: {entity_name}

**Report Date:** {today}

### Executive Summary
Write 2–3 sentences summarizing who this is, what they're involved in, and any risks.

### Key Intelligence by Category

**1. Career / Employment**
- Mention jobs, affiliations, and roles.

**2. Financial / Corporate Ties**
- Business interests, assets, ownerships.

**3. Legal / Regulatory Issues**
- Any sanctions, legal mentions, or red flags.

**4. Academic / Public Presence**
- Degrees, publications, public appearances.

**5. Online / Social Media**
- Platforms, interviews, online influence.

**6. Additional Observations**
- Anything extra that stands out.

### Risk Score
Based on the evidence, estimate the subject’s reputational risk profile.

---

### Task-Wise URLs (Deduplicated, Top 2 Per Task)
{per_task_sources}

---

### Sources (Top 10 Summarized)
{source_summaries}

---

### Citations
{citation_section}
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Failed to generate synthesis: {str(e)}"
