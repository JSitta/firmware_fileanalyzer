# src/data_analysis.py

import pandas as pd
import re


def build_enhanced_dataframe(data):
    """Erstellt einen erweiterten DataFrame mit zusätzlichen Kennzahlen."""
    df = pd.DataFrame(data)

    df["words_per_line"] = df["words"] / df["lines"]
    df["chars_per_word"] = df["chars"] / df["words"]
    df["bytes_per_char"] = df["bytes"] / df["chars"]
    df["error_rate_percent"] = (df["errors"] / df["lines"]) * 100

    df = df.round({
        "words_per_line": 2,
        "chars_per_word": 2,
        "bytes_per_char": 2,
        "error_rate_percent": 2
    })

    return df

def save_dataframe(df, output_path):
    """Speichert den DataFrame als CSV oder JSON."""
    if output_path.endswith(".csv"):
        df.to_csv(output_path, index=False)
    elif output_path.endswith(".json"):
        df.to_json(output_path, orient="records", indent=2)
    else:
        raise ValueError("Nur .csv oder .json Formate sind erlaubt.")

    print(f"✅ Exportiert: {output_path}")
   

def calculate_correlations(data):
    """Berechnet einfache Korrelationen zwischen Kennzahlen."""
    df = pd.DataFrame(data)
    correlations = df[["lines", "words", "chars", "bytes"]].corr()
    return correlations.round(2)


def count_log_entries(text):
    """Zählt INFO, WARN und ERROR Einträge in Logtext."""
    errors = text.lower().count("error")
    warnings = text.lower().count("warn")
    infos = text.lower().count("info")
    return errors, warnings, infos


def classify_errors(text):
    """Klassifiziert typische Fehlerarten in Logtext."""
    text_lower = text.lower()
    classifications = {
        "sensor_error": len(re.findall(r"sensor (array failure|timeout|error|disconnected)", text_lower)),
        "voltage_warning": len(re.findall(r"voltage (fluctuation|drop|issue)", text_lower)),
        "communication_error": len(re.findall(r"(communication link failure|disconnect|link error)", text_lower)),
        "firmware_issue": len(re.findall(r"firmware (update failed|error)", text_lower)),
        "collision_error": len(re.findall(r"(obstacle detected|collision detected)", text_lower))
    }
    return classifications




