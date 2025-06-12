import json
from datetime import datetime
from pathlib import Path

def save_osint_state_to_file(state: dict, entity_name: str):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{entity_name.replace(' ', '_')}_{timestamp}.json"
    output_dir = Path("output_logs")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / filename, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    print(f"📦 OSINT state saved to: {output_dir / filename}")
