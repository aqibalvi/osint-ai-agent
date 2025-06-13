import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def judgement_agent(entity_name: str, raw_report: str, retrievals: dict) -> dict:
    prompt = f"""
You are Claude Opus 4, acting as the **final QA and Risk Assessment agent** in an OSINT AI pipeline.

Your task is to:
1. Verify the report's **factual accuracy** against the provided retrieval evidence.
2. Identify **hallucinations** or unverifiable claims.
3. Check for **contradictions or duplicate information**.
4. Assess **depth and comprehensiveness** of the report.
5. Return an overall **credibility score (1–10)** for the report.
6. Perform a **risk assessment** based on retrieved intelligence:
   - Detect any signals of legal, reputational, or political risk.
   - Assign a **risk score (1–10)**.
   - Classify overall **risk level** as LOW / MEDIUM / HIGH.
   - List all **risk signals** with supporting evidence.
7. Return a **revised version** of the report (if needed) that is more accurate, better cited, and well-organized.
8. Add **footnotes or citations** as needed to clarify provenance or support claims.

---

### Entity: {entity_name}

### Synthesized Report:
{raw_report}

### Retrieval Evidence:
{json.dumps(retrievals, indent=2)}

Respond ONLY in this exact JSON format (no markdown, no explanations):

{{
  "credibility_score": "<1–10>",
  "flagged_issues": ["<issues found in the report>"],
  "risk_assessment": {{
    "risk_score": "<1–10>",
    "verdict": "<LOW | MEDIUM | HIGH>",
    "risk_signals": ["<explanation of any potential risks>"]
  }},
  "revised_report": "<final, improved version of the report>"
}}
"""

    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1800,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()

    # Clean markdown if needed
    if text.startswith("```json") or text.startswith("```"):
        text = text.split("```")[1].strip()

    try:
        result = json.loads(text)
        return {
            "credibility_score": result.get("credibility_score", "N/A"),
            "flagged_issues": result.get("flagged_issues", []),
            "risk_assessment": result.get("risk_assessment", {
                "risk_score": "N/A",
                "verdict": "UNKNOWN",
                "risk_signals": ["Risk assessment not available."]
            }),
            "revised_report": result.get("revised_report", raw_report)
        }
    except Exception as e:
        return {
            "credibility_score": "N/A",
            "flagged_issues": [f"Parsing error: {str(e)}"],
            "risk_assessment": {
                "risk_score": "N/A",
                "verdict": "UNKNOWN",
                "risk_signals": ["Unable to parse risk assessment due to formatting issue."]
            },
            "revised_report": raw_report
        }
