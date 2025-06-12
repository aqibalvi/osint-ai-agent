import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def judgement_agent(entity_name: str, raw_report: str, retrievals: dict) -> dict:
    prompt = f"""
You are Claude Opus 4, acting as the **final QA judgment agent** in an OSINT AI pipeline.

Your task is to:
1. Verify the report's **factual accuracy** against the provided retrieval evidence.
2. Identify **hallucinations** or unverifiable claims.
3. Check for **contradictions or duplicate information**.
4. Assess **depth and comprehensiveness** of the report.
5. Return a **revised report** (if needed) with a final **credibility score (1–10)**.
6. Add **footnotes or citations** if helpful to track information provenance.
7. Note any **missing investigations or weak areas**.

---

### Entity: {entity_name}

### Synthesized Report:
{raw_report}

### Retrieval Evidence:
{json.dumps(retrievals, indent=2)}

Please respond only in this exact JSON format, without any markdown or triple backticks:

{{
  "credibility_score": "<score from 1 to 10>",
  "flagged_issues": ["<summary of any factual error, missing areas, or hallucination>"],
  "revised_report": "<final markdown version of the report with any improvements, citations, and clarifications>"
}}
"""
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1800,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    if text.startswith("```json") or text.startswith("```"):
        text = text.split("```")[1]

    try:
        return json.loads(text)
    except Exception as e:
        return {
            "credibility_score": "N/A",
            "flagged_issues": [f"Parsing error: {str(e)}"],
            "revised_report": raw_report
        }
