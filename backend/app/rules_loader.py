# import json
# from pathlib import Path

# RULES_PATH = Path(__file__).parent / "rules.json"

# def load_rules():
#     if RULES_PATH.exists():
#         with open(RULES_PATH, "r", encoding="utf8") as f:
#             rules = json.load(f)
#         return {r["id"]: r for r in rules}
#     return {}
# rules_loader.py
import json
from pathlib import Path

RULES_PATH = Path(__file__).parent / "rules.json"

def load_rules():
    """
    Load rules.json and return a dict keyed by rule id.
    Expected rules.json: [ { "id": "rule_x", ... }, ... ]
    """
    if not RULES_PATH.exists():
        return {}
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        rules_list = json.load(f)
    # convert to dict for fast lookup
    rules = {r["id"]: r for r in rules_list if "id" in r}
    return rules
