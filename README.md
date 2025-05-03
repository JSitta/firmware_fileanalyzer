# Firmware File Analyzer, Stand: 30.04.2025

![CI](https://github.com/JSitta/firmware_fileanalyzer/actions/workflows/test.yml/badge.svg)

Ein Tool zur Analyse von Firmware-Protokollen, Log-Daten und Fehlerarten.


Ein modulares Analyse- und Visualisierungstool für Textdateien mit Fokus auf Firmware-, Sensordaten- und Robotik-Logs.

---

## 📦 Projektstruktur (aktualisiert)

```
firmware_fileanalyzer/
├── main.py                     # Einstiegspunkt für das CLI
├── requirements.txt           # Projektabhängigkeiten
├── README.md                  # Dieses Dokument
├── tag-*.pdf                  # Tagesjournale
├── data/                      # Eingabedateien (.txt)
├── charts/                    # Visualisierungsausgabe
│   ├── summary/               # Zusammenfassende Charts
│   └── trends/                # Trend-Scatterplots
├── src/                       # Quellcode-Module
│   ├── text_analyzer.py       # Hauptanalyseklasse
│   ├── text_tool.py           # Textoperationen (z.B. Wortzählung)
│   ├── file_reader.py         # Datei-Lesehilfen
│   ├── file_writer.py         # Exportfunktionen
│   ├── visualizer.py          # Visualisierungen (Charts)
│   ├── data_analysis.py       # Erweiterte Auswertungen, Fehlerquoten etc.
│   └── log_util.py            # Logging-Konfiguration
├── tests/                     # Unittests
│   └── test_text_analyzer.py
└── backup/                    # Projekt-Backups
```

---

## ▶️ Verwendung

```bash
# Standardanalyse (mit Tabellen, Plots, Alerts)
python main.py visualize --dir ./data

# Mit optionalem Fehlerquoten-Schwellenwert
python main.py visualize --dir ./data --alert-threshold 5.0

# CSV-/JSON-Export ohne Pandas
python main.py export-basic --dir ./data --output results.csv

# Erweiterte Analyse + Export mit Pandas
python main.py analyze-pandas --dir ./data --export results.json --format json

# Interaktive Textbereinigung + Wortzählung
python main.py clean-text

# Textsuche in allen .txt-Dateien
python main.py search-text --dir ./data "ERROR"

## 🧭 CLI-Befehlsübersicht

### 🔍 Standardanalyse
```bash
python main.py analyze --dir ./data
python main.py analyze-pandas --dir ./data --export report.csv --format csv
python main.py analyze-pandas --dir ./data --export stats.json --format json
python main.py export-basic --dir ./data --output export.csv --format csv

✨ Interaktive Funktionen

python main.py clean-text
python main.py search-text --dir ./data "ERROR"

📊 Visualisierung & Analyse

python main.py visualize --dir ./data --export summary.csv --alert-threshold 10
python main.py visualize-errors --filepath ./data/sensor_data_with_lots_errors.txt
python main.py visualize-errors-all --filepath ./data/sensor_data_with_lots_errors.txt

📄 Fehlerreports & Export

python main.py generate-error-report --filepath ./data/sensor_data_with_lots_errors.txt
python main.py generate-full-error-report --filepath ./data/sensor_data_with_lots_errors.txt
python main.py generate-error-report-zip --filepath ./data/sensor_data_with_lots_errors.txt

## 🧪 Tests ausführen

```bash
# Einzeltest
python -m unittest tests/test_text_analyzer.py

# Alle Tests (wenn erweitert)
python -m unittest discover -s tests
```

---

## 📌 Abhängigkeiten (requirements.txt)

```txt
pandas>=2.2.0
matplotlib>=3.8.0
seaborn>=0.13.0
typer>=0.9.0
click>=8.1.0
rich>=13.7.0
fpdf>=1.7.2
openpyxl>=3.1.0
```

---

## 🔍 Funktionen

- Zählung von Zeilen, Wörtern, Zeichen, Bytes
- Fehlererkennung: INFO / WARN / ERROR
- Fehlerklassifikation: Sensor-, Kommunikations-, Firmwarefehler etc.
- Berechnung der Fehlerquote pro Datei (%-Wert)
- Dynamisches Alert-System mit Schwellenwert
- Visualisierung als Balken, Histogramme, Scatterplots
- Schöne CLI-Ausgabe mit "rich"
- Tagesjournale, Backups, GitHub-ready

---

## 📅 Dokumentation

- Tagesjournale: `tag-<n>-journal.pdf`
- Backups: automatisch via `backup_tool.py`

---

## ✅ Status

Das Projekt ist voll einsatzbereit zur Analyse textbasierter Logdaten im Firmware-/Robotik-Kontext, modular erweiterbar, versioniert und dokumentiert.

Für den produktiven Einsatz oder als Bewerbungsreferenz geeignet.
