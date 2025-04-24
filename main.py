# main.py – Erste Erweiterung vom Einstiegspunkt, argparse wird ersetzt durch typer
# zusätzlich wird die Existenz des Pfades bei analyze überprüft. Eingabe bei clean-text ist
# interaktiv möglich.
# Aufruf: python main.py analyze-pandas --dir <data-directory> --export <file_name> (z.B. report_test.csv)

import typer
import logging
import os
from src.text_tool import remove_whitespace, word_count
from src.log_util import setup_logger
from src.text_analyzer import TextAnalyzer
from typing import Optional

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
        "./data",
        "--dir",
        "-d",
        help="Pfad zum Verzeichnis mit .txt-Dateien"
    ),
    export: str = typer.Option(
        "report.csv",
        "--export",
        "-e",
        help="Pfad zur Ausgabedatei für Statistik (CSV)"
    )
):
    """Analysiert mit pandas-Erweiterung und exportiert als CSV."""
    if not os.path.exists(dir):
        typer.echo(f"❌ Fehler: Verzeichnis nicht gefunden: {dir}")
        raise typer.Exit(code=1)

    analyzer = TextAnalyzer(dir)
    if analyzer.collect_files():
        analyzer.analyze()
        analyzer.report()
        analyzer.report_pandas(export)


if __name__ == "__main__":
    app()
