# src/file_writer.py – Textdatei schreiben
# src/file_writer.py – Exportfunktionen ohne pandas

import pandas as pd
import csv
import json

def export_to_csv(data, path: str) -> None:
    """Exportiert Daten als CSV-Datei. Akzeptiert list[dict] oder pandas.DataFrame."""
    if isinstance(data, pd.DataFrame):
        data = data.to_dict(orient="records")
    if not data:
        print("⚠️ Keine Daten zum Exportieren (CSV).")
        return

    try:
        with open(path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"💾 CSV-Datei erfolgreich exportiert: {path}")
    except Exception as e:
        print(f"❌ Fehler beim CSV-Export: {e}")

def export_to_json(data, path: str) -> None:
    """Exportiert Daten als JSON-Datei. Akzeptiert list[dict] oder pandas.DataFrame."""
    if isinstance(data, pd.DataFrame):
        data = data.copy()
        for col in data.select_dtypes(include=["datetime64[ns]"]):
            data[col] = data[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        data = data.to_dict(orient="records")

    if not data:
        print("⚠️ Keine Daten zum Exportieren (JSON).")
        return

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON-Datei erfolgreich exportiert: {path}")
    except Exception as e:
        print(f"❌ Fehler beim JSON-Export: {e}")



def write_text_file(path, text):
    """Speichert einen Text im UTF-8-Format an einem bestimmten Pfad."""
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(text)
            print(f"✅ Datei erfolgreich gespeichert: {path}")
    except Exception as e:
        print(f"❌ Fehler beim Schreiben in die Datei {path}: {e}")
        