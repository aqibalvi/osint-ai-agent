import json
from datetime import datetime
from pathlib import Path
from agent.state import OSINTState

def save_osint_state_to_file(state: dict, entity_name: str):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{entity_name.replace(' ', '_')}_{timestamp}.json"
    output_dir = Path("output_logs")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / filename, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print(f"📦 OSINT state saved to: {output_dir / filename}")

def load_osint_state_from_file(file_path: str) -> OSINTState:
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
        print("Attempting to load:", file_path)
    return OSINTState(**raw)