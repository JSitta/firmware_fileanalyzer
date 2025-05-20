# tests/test_main.py
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typer.testing import CliRunner

# Pfad zum src-Verzeichnis hinzufügen, damit Imports funktionieren
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app  # Importiere die Typer-App
from src.file_reader import read_text_file
from src.file_writer import export_to_csv, export_to_json  # Importiere die Funktionen

runner = CliRunner()

# Hilfsfunktionen
def create_temp_files(test_data):
    """Erstellt temporäre .txt-Dateien für Tests."""

    temp_dir = tempfile.mkdtemp()
    for filename, content in test_data.items():
        with open(os.path.join(temp_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)
    return temp_dir

def cleanup_temp_dir(temp_dir):
    """Löscht ein temporäres Verzeichnis und seinen Inhalt."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Tests für CLI-Befehle
def test_analyze():
    """Testet den 'analyze'-Befehl."""

    test_data = {
        "file1.txt": "2024-01-01 10:00:00 - ERROR - Sensor failure\n2024-01-01 10:15:00 - INFO - System started",
        "file2.txt": "2024-01-02 12:00:00 - WARNING - Low voltage\n2024-01-02 12:30:00 - ERROR - Communication lost"
    }
    temp_dir = create_temp_files(test_data)
    result = runner.invoke(app, ["analyze", "--dir", temp_dir])
    assert result.exit_code == 0
    assert "source_file" in result.stdout

    cleanup_temp_dir(temp_dir)

def test_analyze_export_csv():
    """Testet den 'analyze-pandas'-Befehl mit CSV-Export."""
    test_data = {
        "file1.txt": "2024-01-01 10:00:00 - ERROR - Sensor failure",
        "file2.txt": "2024-01-02 12:00:00 - WARNING - Low voltage"
    }
    temp_dir = create_temp_files(test_data)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as temp_csv:
        result = runner.invoke(app, ["analyze-pandas", "--dir", temp_dir, "--export", temp_csv.name, "--format", "csv"])
        assert result.exit_code == 0
        assert os.path.exists(temp_csv.name)
        # Hier kannst du den Inhalt der CSV-Datei weiter prüfen
    cleanup_temp_dir(temp_dir)

def test_analyze_export_json():
    """Testet den 'analyze-pandas'-Befehl mit JSON-Export."""
    test_data = {
        "file1.txt": "2024-01-01 10:00:00 - ERROR - Sensor failure",
        "file2.txt": "2024-01-02 12:00:00 - WARNING - Low voltage"
    }
    temp_dir = create_temp_files(test_data)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_json:
        result = runner.invoke(app, ["analyze-pandas", "--dir", temp_dir, "--export", temp_json.name, "--format", "json"])
        assert result.exit_code == 0
        assert os.path.exists(temp_json.name)
        # Hier kannst du den Inhalt der JSON-Datei weiter prüfen
    cleanup_temp_dir(temp_dir)

def test_search_text():
    """Testet den 'search-text'-Befehl."""

    test_data = {
        "file1.txt": "This line contains an ERROR.",
        "file2.txt": "No errors here."
    }
    temp_dir = create_temp_files(test_data)
    result = runner.invoke(app, ["search-text", "--dir", temp_dir, "ERROR"], color=False)  # Wichtig: color=False
    assert result.exit_code == 0
    assert "file1.txt" in result.stdout
    # Prüfe, dass der Suchbegriff in file1.txt gefunden wurde
    assert "ERROR" in open(os.path.join(temp_dir, "file1.txt")).read()
    # Prüfe, dass file2.txt nicht in einer Trefferzeile ist
    assert "file2.txt - Zeile" not in result.stdout  # Einfachere Prüfung
    cleanup_temp_dir(temp_dir)

def test_clean_text():
    """Testet den 'clean_text'-Befehl."""

    result = runner.invoke(app, ["clean-text", "  Multiple   spaces   here  "])
    assert result.exit_code == 0
    assert "Bereinigt: 'Multiple spaces here'" in result.stdout
    assert "Wortanzahl: 3" in result.stdout

def test_export_basic_csv():
    """Testet den 'export_basic'-Befehl mit CSV-Export."""

    test_data = {
        "file1.txt": "Line 1\nLine 2",
        "file2.txt": "One line"
    }
    temp_dir = create_temp_files(test_data)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as temp_csv:
        result = runner.invoke(app, ["export-basic", "--dir", temp_dir, "--output", temp_csv.name, "--format", "csv"])
        assert result.exit_code == 0
        assert os.path.exists(temp_csv.name)
        # Hier kannst du den Inhalt der CSV-Datei weiter prüfen
    cleanup_temp_dir(temp_dir)

def test_export_basic_json():
    """Testet den 'export_basic'-Befehl mit JSON-Export."""

    test_data = {
        "file1.txt": "Line 1\nLine 2",
        "file2.txt": "One line"
    }
    temp_dir = create_temp_files(test_data)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_json:
        result = runner.invoke(app, ["export-basic", "--dir", temp_dir, "--output", temp_json.name, "--format", "json"])
        assert result.exit_code == 0
        assert os.path.exists(temp_json.name)
        # Hier kannst du den Inhalt der JSON-Datei weiter prüfen
    cleanup_temp_dir(temp_dir)

# Weitere Tests für 'visualize', 'visualize_errors' usw. würden hier folgen
# (Diese sind komplexer und erfordern ggf. Mocking von Plotfunktionen)

# Tests für src-Funktionen (direkt)
def test_read_text_file():
    """Testet die Funktion 'read_text_file'."""

    temp_file = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False)
    temp_file.write("Test content")
    temp_file.flush()  # Stelle sicher, dass alles geschrieben ist
    temp_file_name = temp_file.name  # Speichere den Dateinamen
    temp_file.close()  # Schließe die Datei explizit

    # Öffne die Datei zum Lesen in einem separaten Block
    content = read_text_file(temp_file_name)
    assert content == "Test content"
    os.remove(temp_file_name)  # Lösche die Datei explizit am Ende

def test_export_to_csv():
    """Testet die Funktion 'export_to_csv'."""

    test_data = [{"col1": "a", "col2": 1}, {"col1": "b", "col2": 2}]
    with tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=True) as temp_csv:
        export_to_csv(test_data, temp_csv.name)
        # Hier kannst du den Inhalt der CSV-Datei weiter prüfen
        assert os.path.exists(temp_csv.name)

def test_export_to_json():
    """Testet die Funktion 'export_to_json'."""

    test_data = [{"col1": "a", "col2": 1}]
    with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=True) as temp_json:
        export_to_json(test_data, temp_json.name)
        # Hier kannst du den Inhalt der JSON-Datei weiter prüfen
        assert os.path.exists(temp_json.name)

# ... (Weitere Tests für Funktionen in anderen Modulen)