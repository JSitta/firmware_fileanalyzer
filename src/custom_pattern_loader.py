import json
import re
from pathlib import Path
from typing import Dict

def load_custom_patterns(json_path: str) -> Dict[str, str]:
    """
    Lädt ein JSON mit Fehlerklassen-Vorschlägen und erzeugt Regex-Muster.
    Beispiel: "can-bus timeout on channel" → r"can\s*-?bus\s+timeout\s+on\s+channel"
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {json_path}")

    with open(path, "r", encoding="utf-8") as f:
        suggestions = json.load(f)

    pattern_dict = {}
    for label in suggestions:
        words = label.strip().lower().split()
        regex = r"\\s+".join(re.escape(word) for word in words)
        regex = regex.replace("can\\s+bus", "can\\s*-?bus")  # optional: Sonderfallhandling
        pattern_dict[label.replace(" ", "_")] = rf"{regex}"

    return pattern_dict
