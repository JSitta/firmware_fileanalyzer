# src/data_analysis.py

import pandas as pd
import re
from datetime import datetime
from src.custom_classifier import classify_custom_error


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


def detect_threshold_warnings(text):
    """
    Sucht numerische Temperaturwerte > 75 °C im Text.
    Gibt Zähler für 'overheating_warning' zurück.
    """
    overheating_count = 0
    pattern = r"Temperature:\s*([0-9]+(?:\.[0-9]+)?)"
    matches = re.findall(pattern, text)
    for value in matches:
        try:
            if float(value) > 75.0:
                overheating_count += 1
        except ValueError:
            continue
    return {"overheating_warning": overheating_count}

def detect_voltage_warnings(text):
    """
    Sucht numerische Spannungseinträge < 11.0 V im Text.
    Gibt Zähler für 'low_voltage_warning' zurück.
    """
    low_voltage_count = 0
    # Erkenne z. B. "Voltage: 10.5", "Voltage drop detected: 9.51V", "low voltage 10.1V"
    pattern = r"(?i)(?:voltage[^\d\n]{0,20})?([0-9]+(?:\.[0-9]+)?)\s?v"
    matches = re.findall(pattern, text)
    for value in matches:
        try:
            if float(value) < 11.0:
                low_voltage_count += 1
        except ValueError:
            continue
    return {"low_voltage_warning": low_voltage_count}


def parse_log_to_dataframe(text, classify: bool = True):
    """
    Extrahiert Logzeilen in strukturierter Form (timestamp, level, message)
    und gibt einen DataFrame zurück.
    """

    pattern = re.compile(
        r"\[?(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]?\s+(?P<level>\w+)\s+(?P<message>.+)"
    )

    
    records = []
    error_patterns = {
        "sensor_error": r"sensor (array failure|timeout|error|disconnected)",
        "voltage_warning": r"voltage (fluctuation|drop|issue)",
        "communication_error": r"(communication link failure|disconnect|link error)",
        "firmware_issue": r"firmware (update failed|error)",
        "collision_error": r"(obstacle detected|collision detected)"
    } if classify else {}
    for line in text.splitlines():
        line = line.strip()
        match = pattern.search(line)
        if match:
            data = match.groupdict()
            try:
                data["timestamp"] = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if classify:
                msg = data["message"].lower()
                for error_type, regex in error_patterns.items():
                    if re.search(regex, msg):
                        data["error_type"] = error_type
                        break
                else:
                    data["error_type"] = classify_custom_error(data["message"])
            records.append(data)
    df = pd.DataFrame(records)

    # Wenn keine Klassifikation: typische Phrasen auswerten
    if not classify and not df.empty:
        df["message_key"] = df["message"].str.lower().str.extract(r"([a-z\- ]+)")
        top_phrases = df["message_key"].value_counts().head(10)
        print("\n🔍 Häufigste Nachrichtentypen (Top 10):")
        print(top_phrases)
        df.attrs["suggested_classes"] = top_phrases

    print(df)
    return df
