# Firmware File Analyzer, Stand: 05.05.2025

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

## ▶️ Verwendung

# CLI-Befehlsübersicht – Firmware File Analyzer

Dieses Skript bietet verschiedene Befehle zur Analyse, Bearbeitung und Visualisierung von Textdateien.

## Standardanalyse (Basisfunktionen)

### `analyze`,analyze-pandas, export-basic, clean-text, search-text, visualize, 
### visualize-errors, visualize-errors-all


```bash
python main.py analyze --dir <Pfad> [--format <Format>] [--export <Exportdatei>]
python main.py analyze-pandas --dir <Pfad> --export <Exportdatei> --format <Format>
python main.py export-basic --dir <Pfad> --output <Zieldatei> --format <Format>
python main.py clean-text [<Text>]
python main.py search-text --dir <Pfad> <Suchbegriff>
python main.py visualize --dir <Pfad> [--export <Exportdatei>] [--alert-threshold <Schwelle>]
python main.py visualize-errors --filepath <Dateipfad>
python main.py visualize-errors-all --filepath <Dateipfad>

## Fehlerreports (Export&PDF)

python main.py generate-error-report --filepath <Dateipfad>
python main.py generate-full-error-report --filepath <Dateipfad>
python main.py generate-error-report-zip --filepath <Dateipfad>

Kritische Fehlerzeitfenster filtern

python main.py find-critical-errors --filepath <Dateipfad> --error-type <Fehlertyp> --threshold <Schwelle>

Weitere Funktionen

python main.py publish-docs
python main.py compare-logs --directory <Verzeichnis>
python main.py plot-error-comparison-chart --directory <Verzeichnis>
python main.py plot-error-heatmap-chart --directory <Verzeichnis>
python main.py interactive-report

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
