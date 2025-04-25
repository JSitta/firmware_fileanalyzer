# main.py – Erste Erweiterung vom Einstiegspunkt, argparse wird ersetzt durch typer
# zusätzlich wird die Existenz des Pfades bei analyze überprüft. Eingabe bei clean-text ist
# interaktiv möglich.
# Aufruf: python main.py analyze-pandas --dir <data-directory> --export <file_name> (z.B. report_test.csv) --format csv
#         python main.py analyze-pandas --dir <data-directory> --export <file_name> (z.B. stats.json) --format json

import typer
import logging
import os
from src.text_tool import remove_whitespace, word_count
from src.file_writer import export_to_csv, export_to_json
from src.file_reader import read_text_file
from src.log_util import setup_logger
from src.text_analyzer import TextAnalyzer
from typing import Optional
from rich import print as rprint
from rich.text import Text

app = typer.Typer()
setup_logger()

@app.command()
def analyze(
    dir: str = typer.Option(
        "./data",
        "--dir",
        "-d",
        help="Pfad zum Verzeichnis mit .txt-Dateien"
    )
):
    """Analysiert ein Verzeichnis mit .txt-Dateien."""
    if not os.path.exists(dir):
        typer.echo(f"❌ Fehler: Verzeichnis nicht gefunden: {dir}")
        raise typer.Exit(code=1)

    analyzer = TextAnalyzer(dir)
    if analyzer.collect_files():
        analyzer.analyze()
        analyzer.report()
    
@app.command()
def search_text(
    dir: str = typer.Option("./data", "--dir", "-d", help="Verzeichnis mit .txt-Dateien"),
    term: str = typer.Argument(..., help="Suchbegriff (nicht case-sensitiv)")
):
    """Durchsucht alle .txt-Dateien im Verzeichnis nach einem Begriff (case-insensitive, farbig hervorgehoben)."""
    if not os.path.exists(dir):
        typer.echo(f"❌ Fehler: Verzeichnis nicht gefunden: {dir}")
        raise typer.Exit(code=1)

    term_lower = term.lower()
    match_found = False

    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            path = os.path.join(dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, start=1):
                        if term_lower in line.lower():
                            if not match_found:
                                rprint(f"\n[bold green]🔍 Ergebnisse für Suchbegriff:[/] '[bold yellow]{term}[/]'\n")
                                match_found = True

                            # farbiges Hervorheben des Treffers
                            line_text = Text(line.strip(), style="white")
                            start = line.lower().find(term_lower)
                            end = start + len(term)
                            if start >= 0:
                                line_text.stylize("bold red on white", start, end)

                            rprint(f"[cyan]📄 {filename}[/] – Zeile {i}: {line_text}")
            except Exception as e:
                typer.echo(f"⚠️ Fehler beim Lesen von {filename}: {e}")

    if not match_found:
        typer.echo(f"❌ Keine Treffer für '{term}' in {dir}")

@app.command()
def clean_text(
    text: Optional[str] = typer.Argument(
        None,
        help="Text, der bereinigt und analysiert werden soll"
    )
):
    """Entfernt überflüssige Leerzeichen und zählt Wörter."""
    if text is None:
        text = typer.prompt("🔤 Bitte gib einen Text ein")

    cleaned = remove_whitespace(text)
    print(f"Bereinigt: '{cleaned}'")
    print(f"Wortanzahl: {word_count(cleaned)}")
    logging.info("Textoperation durchgeführt: remove_whitespace + word_count")


@app.command()
def analyze_pandas(
    dir: str = typer.Option(
        "./data", "--dir", "-d",
        help="Pfad zum Verzeichnis mit .txt-Dateien"
    ),
    export: str = typer.Option(
        "report.csv", "--export", "-e",
        help="Pfad zur Ausgabedatei"
    ),
    format: str = typer.Option(
        "csv", "--format", "-f",
        help="Exportformat: csv oder json"
    )
):
    """Analysiert mit pandas-Erweiterung und exportiert als CSV oder JSON."""
    if not os.path.exists(dir):
        typer.echo(f"❌ Fehler: Verzeichnis nicht gefunden: {dir}")
        raise typer.Exit(code=1)

    analyzer = TextAnalyzer(dir)
    if analyzer.collect_files():
        analyzer.analyze()
        analyzer.report()
        analyzer.report_pandas(export_path=export, file_format=format)

@app.command()
def export_basic(
    dir: str = typer.Option("./data", "--dir", "-d", help="Verzeichnis mit .txt-Dateien"),
    output: str = typer.Option("export_light.csv", "--output", "-o", help="Ziel-Dateiname"),
    format: str = typer.Option("csv", "--format", "-f", help="Exportformat: csv oder json")
):
    """Exportiert Analyseergebnisse ohne pandas – als CSV oder JSON."""
    if not os.path.exists(dir):
        typer.echo(f"❌ Fehler: Verzeichnis nicht gefunden: {dir}")
        raise typer.Exit(code=1)

    # 🧠 Dateien analysieren wie in TextAnalyzer, aber leichtgewichtig:
    stats = []
    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            path = os.path.join(dir, filename)
            text = read_text_file(path)
            if text:
                stats.append({
                    "filename": filename,
                    "lines": text.count('\n') + 1,
                    "words": word_count(text),
                    "chars": len(text),
                    "bytes": os.path.getsize(path)
                })

    # 📦 Export je nach Format:
    if format == "json":
        export_to_json(stats, output)
    else:
        export_to_csv(stats, output)

if __name__ == "__main__":
    app()
