# README.md – Projektbeschreibung

"""
Python Journey – Firmware Engineer

Dieses Projekt enthält ein modulares Analysetool für Textdateien zur Vorbereitung auf eine Tätigkeit als Firmware Integration Engineer (z. B. bei Tesla).

📦 Projektstruktur:

├── main.py                  # Einstiegspunkt für das CLI-Tool
├── src/                    # Quellcode-Module
│   ├── text_analyzer.py    # Hauptklasse für Analyseprozesse
│   ├── text_tool.py        # Hilfsfunktionen zur Textbearbeitung
│   ├── file_reader.py      # Datei-Lesefunktion mit Fehlerbehandlung
│   ├── file_writer.py      # Datei-Schreibfunktion
│   └── log_util.py         # Logging-Konfiguration
├── tests/                  # Unittests mit unittest
│   └── test_text_analyzer.py
├── data/                   # Beispiel- oder Testdaten
├── requirements.txt        # Paketabhängigkeiten
└── README.md               # Dieses Dokument

▶️ Verwendung:

    python main.py --dir ./data
    python main.py analyze-pandas --dir <data-directory> --export <file_name> (z.B. report_test.csv) --format csv
    python main.py analyze-pandas --dir <data-directory> --export <file_name> (z.B. stats.json) --format json


🧪 Tests ausführen:

    python -m unittest tests/test_text_analyzer.py

📌 Abhängigkeiten:
- Python ≥ 3.10
- (Optional für spätere Erweiterung: typer, click)
"""
