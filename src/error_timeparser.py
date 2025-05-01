import re
from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd


# Fehlerarten und zugehörige Schlüsselwörter
type_keywords = {
    "sensor_error": ["sensor failed", "temperature fault"],
    "voltage_warning": ["voltage drop", "low voltage"],
    "communication_error": ["timeout", "communication lost", "no response", "can-bus"],
    "firmware_issue": ["firmware exception", "assertion failed"],
    "collision_error": ["collision", "obstacle"]
}


def extract_timestamp(line: str) -> Optional[datetime]:
    pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
    match = re.search(pattern, line)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    return None


def classify_error_type(line: str) -> str:
    line_lower = line.lower()
    for error_type, keywords in type_keywords.items():
        for keyword in keywords:
            if keyword in line_lower:
                return error_type
    if "error" in line_lower:
        return "generic_error"
    return "info"


def build_error_dataframe(lines: List[str]) -> pd.DataFrame:
    records = []
    for line in lines:
        ts = extract_timestamp(line)
        error_type = classify_error_type(line)
        if ts and error_type != "info":
            # Nur Fehler und Warnungen in den DataFrame aufnehmen
            records.append({"timestamp": ts, "error_type": error_type})

    return pd.DataFrame(records)


# Testausgabe wenn direkt ausgeführt
if __name__ == "__main__":
    with open("../app.log", encoding="utf-8") as f:
        lines = f.readlines()
        df = build_error_dataframe(lines)
        print(df.head())
        #print(df["error_type"].value_counts())
       # print(df["error_type"].value_counts(normalize=True) * 100)