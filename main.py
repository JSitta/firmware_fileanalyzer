# main.py – Erste Erweiterung vom Einstiegspunkt, argparse wird ersetzt durch typer

import typer
import logging
from src.text_tool import remove_whitespace, word_count
from src.log_util import setup_logger
from src.text_analyzer import TextAnalyzer

app = typer.Typer()
setup_logger()

@app.command()
def analyze(dir: str = "./data"):
    """Analysiert ein Verzeichnis mit .txt-Dateien."""
    analyzer = TextAnalyzer(dir)
    if analyzer.collect_files():
        analyzer.analyze()
        analyzer.report()

@app.command()
def clean_text(text: str):
    """Entfernt überflüssige Leerzeichen und zählt Wörter."""
    cleaned = remove_whitespace(text)
    print(f"Bereinigt: '{cleaned}'")
    print(f"Wortanzahl: {word_count(cleaned)}")
    logging.info("Textoperation durchgeführt: remove_whitespace + word_count")

if __name__ == "__main__":
    app()
