import re
from typing import List, Dict

def detect_red_flags(text: str) -> List[Dict[str, str]]:
    red_flags = [
        {"pattern": r"\b(indefinite|perpetual)\b", "risk": "Unclear or unlimited duration obligation"},
        {"pattern": r"\bwithout cause\b", "risk": "Can fire/evict you with no reason"},
        {"pattern": r"assign(\\s+all)?\\s+(inventions|IP|intellectual property)", "risk": "You may lose your IP"},
        {"pattern": r"liable for.*damages|responsible for all.*damages", "risk": "You pay all damage costs"},
        {"pattern": r"landlord.*terminate.*any time", "risk": "Landlord can evict you unfairly"},
        {"pattern": r"penalty of.*\\$\\d+", "risk": "Big penalty fees"},
        {"pattern": r"non[- ]?compete", "risk": "Can't work for similar jobs"},
        {"pattern": r"no refund", "risk": "No refund if things go wrong"}
    ]
    results = []
    seen = set()
    for rule in red_flags:
        for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
            clause = match.group(0).strip()
            if (clause, rule["risk"]) not in seen:
                seen.add((clause, rule["risk"]))
                results.append({"clause": clause, "risk": rule["risk"]})
    return results
