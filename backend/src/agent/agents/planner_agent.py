#backend/src/agent/agents/planner_agent.py

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def planner_agent(entity_type: str, entity_name: str, keywords: list, affiliation: str, location: str) -> list:
    prompt = f"""
You are an OSINT task planner.

Generate 8 **web-searchable** investigation tasks for:
- Entity: {entity_name} ({entity_type})
- Keywords: {', '.join(keywords)}
- Affiliation: {affiliation}
- Location: {location}

Include diverse areas like:
- LinkedIn role at {affiliation}
- Local {location} registries or residency databases
- News/media mentions in {location}
- Career, business, legal, financial, academic, social presence

Keep each task:
- Specific
- Actionable
- Factual
- Likely to yield results online

Respond ONLY with a JSON array of strings:
[
  "Search LinkedIn for current role of {entity_name} at {affiliation}",
  "Check {location} business registries for companies linked to {entity_name}",
  ...
]
"""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=200,
        temperature=0.5,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip().strip("```json").strip("```")
    tasks = eval(raw)
    return tasks[:8]
