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
from src.visualizer import plot_analysis, plot_trends
from src.data_analysis import (build_enhanced_dataframe, save_dataframe,
                               calculate_correlations, count_log_entries, classify_errors)
from typing import Optional
from rich import print as rprint
from rich.text import Text
from rich.console import Console
from rich.table import Table


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


@app.command()
def visualize(
    dir: str = "./data",
    export: str = typer.Option(None, "--export", "-e", help="Exportiere erweiterten DataFrame (Pfad zu .csv oder .json)"),
    alert_threshold: float = typer.Option(10.0, "--alert-threshold", "-a", help="Fehlerquote-Schwelle für Warnungen (%)")
):
    """Erstellt Visualisierungen auf Basis der .txt-Analysen."""
    analyzer = TextAnalyzer(dir)
    if analyzer.collect_files():
        analyzer.analyze()
        data = []
        for filename in analyzer.txt_files:
            path = os.path.join(dir, filename)
            text = read_text_file(path)
            errors, warnings, infos = count_log_entries(text) if text else (0, 0, 0)
            error_classes = classify_errors(text) if text else {}

            # Berechnung der Statistiken
            data.append({
                "filename": filename,
                "lines": text.count('\n') + 1 if text else 0,
                "words": word_count(text) if text else 0,
                "chars": len(text) if text else 0,
                "bytes": os.path.getsize(path) if os.path.exists(path) else 0,
                "errors": errors,
                "warnings": warnings,
                "infos": infos,
                "sensor_errors": error_classes.get("sensor_error", 0),
                "voltage_warnings": error_classes.get("voltage_warning", 0),
                "communication_errors": error_classes.get("communication_error", 0),
                "firmware_issues": error_classes.get("firmware_issue", 0),
                "collision_errors": error_classes.get("collision_error", 0)
            })
        plot_analysis(data)

        # Erstellen des erweiterten DataFrames
        enhanced_df = build_enhanced_dataframe(data)
        # Ausgabe des erweiterten DataFrames im Terminal
        #typer.echo("\n📈 Erweiterte Analyse:\n")
        #typer.echo(enhanced_df.to_string(index=False))

        console = Console()

        # Ausgabe schöner formatieren mit Rich-Table
        table = Table(title="📈 Erweiterte Analyse der Textdateien", header_style="bold cyan")

        # Spalten dynamisch aus dem DataFrame übernehmen
        for col in enhanced_df.columns:
            table.add_column(str(col), justify="right")

        # Zeilen ausfüllen
        for _, row in enhanced_df.iterrows():
            row_values = []
            for col_name in enhanced_df.columns:
                value = row[col_name]
                if col_name == "error_rate_percent" and value > 10:
                    row_values.append(f"[bold red]{value:.2f} ⚠️[/bold red]")
                else:
                    row_values.append(str(value))
            table.add_row(*row_values)


        console.print(table)

        plot_trends(data)
        correlations = calculate_correlations(data)

        console = Console()
        console.print("\n📊 [bold magenta]Korrelationsmatrix:[/bold magenta]")
        console.print(correlations)

        # Zusammenfassung: Anzahl kritischer Dateien
        critical_files = enhanced_df[enhanced_df["error_rate_percent"] > alert_threshold]
        
        if not critical_files.empty:
            console.print(f"\n[bold red]⚠️ {len(critical_files)} Datei(en) mit Fehlerquote > {alert_threshold:.1f} % erkannt:[/bold red]")
            for filename in critical_files["filename"]:
                console.print(f" - [yellow]{filename}[/yellow]")
        else:
            console.print(f"\n[bold green]✅ Keine kritischen Fehlerquoten über {alert_threshold:.1f} % erkannt.[/bold green]")


        # Export, wenn Option angegeben ist
        if export:
            save_dataframe(enhanced_df, export)

        typer.echo("✅ Visualisierungen wurden erfolgreich erstellt und gespeichert.")



if __name__ == "__main__":
    app()
