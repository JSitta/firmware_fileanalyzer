# main.py – Stand: 02.05.2025
# ------------------------------------------------------------
# 🔧 CLI-Befehlsübersicht – Firmware File Analyzer
#
# Standardanalyse (Basisfunktionen)
# ----------------------------------
# python main.py analyze --dir ./data
# python main.py analyze-pandas --dir ./data --export report.csv --format csv
# python main.py analyze-pandas --dir ./data --export stats.json --format json
# python main.py export-basic --dir ./data --output export.csv --format csv
#
# Interaktive Funktionen
# -----------------------
# python main.py clean-text
# python main.py search-text --dir ./data "ERROR"
#
# Visualisierung & erweiterte Analyse
# -----------------------------------
# python main.py visualize --dir ./data --export summary.csv --alert-threshold 10
# python main.py visualize-errors --filepath ./data/sensor_data_with_lots_errors.txt
# python main.py visualize-errors-all --filepath ./data/sensor_data_with_lots_errors.txt
#
# Fehlerreports (Export & PDF)
# -----------------------------
# python main.py generate-error-report --filepath ./data/sensor_data_with_lots_errors.txt
# python main.py generate-full-error-report --filepath ./data/sensor_data_with_lots_errors.txt
# python main.py generate-error-report-zip --filepath ./data/sensor_data_with_lots_errors.txt
#
# Kritische Fehlerzeitfenster filtern
# ------------------------------------
# python main.py find-critical-errors --filepath ./data/sensor_data_with_lots_errors.txt --error-type firmware_issue --threshold 4
# ------------------------------------------------------------


import typer
import logging
import os
from src.text_tool import remove_whitespace, word_count
from src.file_writer import export_to_csv, export_to_json
from src.file_reader import read_text_file
from src.log_util import setup_logger
from src.text_analyzer import TextAnalyzer
from src.visualizer import plot_analysis, plot_trends, plot_error_types
from src.data_analysis import (build_enhanced_dataframe, save_dataframe,
                               calculate_correlations, count_log_entries, classify_errors)
from src.error_visualizer import (plot_error_timecourse, plot_error_heatmap, export_error_report_to_pdf, export_report_as_zip,
                                  detect_critical_error_windows, publish_reports_to_docs, compare_error_logs,
                                  plot_error_comparison, plot_error_heatmap_logs)
from src.error_timeparser import classify_error_type, extract_timestamp, build_error_dataframe
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
                "collision_errors": error_classes.get("collision_error", 0),
                "sensor_error":     error_classes.get("sensor_error", 0),
                "voltage_warning":  error_classes.get("voltage_warning", 0),
                "communication_error": error_classes.get("communication_error", 0),
                "firmware_issue":   error_classes.get("firmware_issue", 0),
                "collision_error":  error_classes.get("collision_error", 0)
            })
        plot_analysis(data)
        plot_error_types(data)
        # Ausgabe der Statistiken im Terminal       

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


        # Fehlerzeitverlauf analysieren
@app.command()
def visualize_errors(
    filepath: str = "./data/sensor_data_with_lots_errors.txt"
):
    """Visualisiert den Fehlerzeitverlauf einer Logdatei mit Zeitstempeln und Fehlerarten."""
    if not os.path.exists(filepath):
        print(f"Datei nicht gefunden: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    df = build_error_dataframe(lines)

    # Info-Zeilen ggf. filtern
    df = df[df["error_type"] != "info"]

    # Zeitverlauf plotten
    plot_error_timecourse(df)



@app.command()
def visualize_errors_all(
    filepath: str = "./data/sensor_data_with_lots_errors.txt"
):
    """
    Führt vollständige Fehlerzeit-Visualisierung aus (Balken, Linie, Heatmap).
    """
    if not os.path.exists(filepath):
        print(f"Datei nicht gefunden: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    df = build_error_dataframe(lines)
    df = df[df["error_type"] != "info"]

    plot_error_timecourse(df)
    plot_error_heatmap(df)

@app.command()
def generate_error_report(
    filepath: str = "./data/sensor_data_with_lots_errors.txt"
):
    """
    Erstellt vollständige Fehlerauswertung inkl. PDF-Report.
    """
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    df = build_error_dataframe(lines)
    df = df[df["error_type"] != "info"]

    plot_error_timecourse(df)
    export_error_report_to_pdf()

@app.command()
def generate_full_error_report(
    filepath: str = "./data/sensor_data_with_lots_errors.txt"
):
    """
    Erstellt vollständige Fehleranalyse mit PDF-Report inklusive Heatmap und kritischer Zusammenfassung.
    """
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    df = build_error_dataframe(lines)
    df = df[df["error_type"] != "info"]

    plot_error_timecourse(df)
    plot_error_heatmap(df)
    export_error_report_to_pdf(df)

@app.command()
def generate_error_report_zip(
    filepath: str = "./data/sensor_data_with_lots_errors.txt"
):
    """
    Erstellt vollständigen Fehlerbericht inkl. ZIP-Export aller Ausgabedateien.
    """
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    df = build_error_dataframe(lines)
    df = df[df["error_type"] != "info"]

    plot_error_timecourse(df)
    plot_error_heatmap(df)
    export_error_report_to_pdf(df)
    export_report_as_zip()

@app.command()
def find_critical_errors(
    filepath: str = "./data/sensor_data_with_lots_errors.txt",
    error_type: str = "firmware_issue",
    threshold: int = 3
):
    """
    Zeigt alle Stunden, in denen ein bestimmter Fehlertyp häufiger als 'threshold' auftrat.
    """
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    df = build_error_dataframe(lines)
    df = df[df["error_type"] != "info"]

    filtered = detect_critical_error_windows(df, threshold=threshold)
    result = filtered[filtered["error_type"] == error_type]

    if result.empty:
        print(f"Keine Zeitfenster mit mehr als {threshold} Vorkommen von '{error_type}' gefunden.")
    else:
        print(f"⚠️ Kritische Zeitfenster für '{error_type}' (≥ {threshold} Fehler):\n")
        print(result.to_string(index=False))


@app.command()
def publish_docs():
    """
    Kopiert alle aktuellen Report-Dateien nach docs/reports zur Veröffentlichung.
    """
    publish_reports_to_docs()


@app.command()
def compare_logs(directory: str = "./data"):
    """
    Vergleicht Fehlerarten über mehrere Logdateien im angegebenen Verzeichnis.
    """
    df = compare_error_logs(directory)
    print(df)

@app.command()
def plot_error_comparison_chart(directory: str = "./data"):
    """
    Erstellt einen gruppierten Balkenplot zur Fehlerverteilung pro Logdatei.
    """
    df = compare_error_logs(directory)
    plot_error_comparison(df)

@app.command()
def plot_error_heatmap_chart(directory: str = "./data"):
    """
    Erstellt eine Heatmap der Fehlerarten über mehrere Logdateien.
    """
    df = compare_error_logs(directory)
    plot_error_heatmap_logs(df)


@app.command()
def interactive_report():
    """Geführter Ablauf zur Erstellung eines Fehler-Reports aus mehreren Logdateien."""
    typer.echo("🧭 Interaktiver Reportgenerator gestartet")
    directory = typer.prompt("📁 Verzeichnis mit Logdateien", default="./data")
    df = compare_error_logs(directory)

    if typer.confirm("🔍 Fehlervergleich anzeigen?"):
        typer.echo(df)

    if typer.confirm("📊 Gruppierten Balkenplot erstellen?"):
        plot_error_comparison(df)

    if typer.confirm("🔥 Heatmap erstellen?"):
        plot_error_heatmap_logs(df)

    if typer.confirm("📄 PDF-Report exportieren?"):
        export_error_report_to_pdf(df)

    if typer.confirm("🗜️ ZIP-Export erzeugen?"):
        export_report_as_zip()

    if typer.confirm("🌐 In docs/reports veröffentlichen?"):
        publish_reports_to_docs()

    typer.echo("✅ Interaktive Reportgenerierung abgeschlossen.")




if __name__ == "__main__":
    app()
