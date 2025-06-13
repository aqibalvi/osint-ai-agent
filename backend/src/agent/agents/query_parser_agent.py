#backend/src/agent/agents/query_parser_agent
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import json

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def query_parser_agent(query: str) -> dict:
    prompt = f"""
You are an OSINT query parser.

Extract structured metadata from the natural language query below. Output only a **valid JSON object**.

Required fields:
- "entity_type": "person" or "organization"
- "entity_name": full name of person or org
- "keywords": important investigation topics (list of 3–6 strings)
- "affiliation": known workplace or organization (if any)
- "location": primary place of activity or residence
- "nationality": if stated clearly

Query: "{query}"

Respond ONLY with JSON like:
{{
  "entity_type": "person",
  "entity_name": "Muhammad Aqib Iqbal",
  "keywords": ["AI", "Turing", "LinkedIn", "Oman"],
  "affiliation": "Turing",
  "location": "Oman",
  "nationality": "Pakistani"
}}
"""
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()

    try:
        # Try loading directly
        return json.loads(text)
    except json.JSONDecodeError:
        # Try cleaning common wrappers
        for clean in [
            text.strip("```json").strip("```").strip(),
            text.replace("```json", "").replace("```", "").strip(),
            text.split("```")[-1].strip()
        ]:
            try:
                return json.loads(clean)
            except json.JSONDecodeError:
                continue
        raise ValueError(f"❌ Failed to parse structured JSON from Claude:\n{text}")
