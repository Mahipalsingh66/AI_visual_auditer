import json
from pathlib import Path

RULES_PATH = Path(__file__).parent / "rules.json"

def load_rules():
    if RULES_PATH.exists():
        with open(RULES_PATH, "r", encoding="utf8") as f:
            rules = json.load(f)
        return {r["id"]: r for r in rules}
    return {}
