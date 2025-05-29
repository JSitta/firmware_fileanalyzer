# main.py – Stand: 23.05.2025
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
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.text_tool import remove_whitespace, word_count
from src.file_writer import export_to_csv, export_to_json
from src.file_reader import read_text_file
from src.log_util import setup_logger
from src.text_analyzer import TextAnalyzer
from src.visualizer import (plot_analysis, plot_trends, plot_error_types)
from src.data_analysis import (build_enhanced_dataframe, save_dataframe, detect_voltage_warnings, parse_log_to_dataframe,
                               detect_threshold_warnings, calculate_correlations, count_log_entries, classify_errors)
from src.error_visualizer import (plot_error_timecourse, plot_error_heatmap, export_error_report_to_pdf, export_report_as_zip,
                                  detect_critical_error_windows, publish_reports_to_docs, compare_error_logs, compare_custom_error_logs,
                                  plot_error_comparison, plot_error_heatmap_logs, export_emba_report_to_pdf)
from src.error_timeparser import classify_error_type, extract_timestamp, build_error_dataframe
from src.emba_parser import (extract_summary_from_index, extract_cves_auto, extract_cves_from_f17, plot_top_cve_components)
from typing import Optional
from rich import print as rprint
from rich.text import Text
from rich.console import Console
from rich.table import Table


app = typer.Typer()
setup_logger()

@app.command()
def analyze(
    dir: str = typer.Option("./data","--dir","-d",help="Pfad zum Verzeichnis mit .txt-Dateien"),
    format: str = typer.Option("csv", help="Exportformat: csv oder json"),
    export: Optional[str] = typer.Option(None, help="Pfad zur Exportdatei (optional)")
):
    """Analysiert ein Verzeichnis mit .txt-Dateien."""
    all_entries = []
    for fname in os.listdir(dir):
        if fname.endswith(".txt"):
            path = os.path.join(dir, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            lines = content.splitlines()
            error_df = build_error_dataframe(lines)
            if error_df.empty:
                continue
            error_df["source_file"] = fname
            all_entries.append(error_df)

    if not all_entries:
        print("⚠️ Keine gültigen Fehlerdaten gefunden.")
        raise typer.Exit()

    result_df = pd.concat(all_entries)
    print(result_df.head())


    if export:
        export_dir = os.path.dirname(export)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)
        if format == "csv":
            export_to_csv(result_df, export)
            print(f"✅ CSV exportiert: {export}")
        elif format == "json":
            export_to_json(result_df, export)
            print(f"✅ JSON exportiert: {export}")
        else:
            print(f"❌ Unbekanntes Format: {format}")

    
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
def check_firmware_status(
    filepath: str = typer.Option(..., help="Pfad zur Logdatei (.txt) mit Zeitstempeln und Fehlern")
):
    """
    Prüft automatisch, ob die Firmware anhand des Fehlerlogs für das Deployment geeignet ist.
    """
    from src.error_timeparser import build_error_dataframe
    from src.emba_parser import evaluate_firmware_acceptance

    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        raise typer.Exit()

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    df = build_error_dataframe(lines)
    status, reason = evaluate_firmware_acceptance(df)

    print("\n📋 Deployment-Entscheidung:")
    if status:
        print("✅ Firmware FREIGEGEBEN")
    else:
        print("❌ Firmware BLOCKIERT")
    print(f"Begründung: {reason}")


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
            threshold_classes = detect_threshold_warnings(text) if text else {}
            voltage_classes = detect_voltage_warnings(text) if text else {}

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
                "collision_error":  error_classes.get("collision_error", 0),
                "overheating_warning": threshold_classes.get("overheating_warning", 0),
                "low_voltage_warning": voltage_classes.get("low_voltage_warning", 0)
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


@app.command()
def analyze_emba(
    filepath: str = typer.Option(..., help="Pfad zur index.html von EMBA"),
    export: Optional[str] = typer.Option(None, help="Pfad zur Exportdatei (csv/json)")
):
    """Analysiert EMBA index.html und extrahiert relevante Sicherheitsergebnisse."""
    from src.emba_parser import extract_summary_from_index

    df = extract_summary_from_index(filepath)
    print(df)

    if export:
        from src.file_writer import export_to_csv, export_to_json
        if export.endswith(".csv"):
            export_to_csv(df, export)
        elif export.endswith(".json"):
            export_to_json(df, export)
        else:
            print("❌ Nur .csv oder .json unterstützt.")


@app.command()
def analyze_emba_cves(
    filepath: str = typer.Option(..., help="Pfad zur index.html oder f17_cve_bin_tool.html"),
    export: Optional[str] = typer.Option(None, help="Exportpfad für CSV"),
    min_cves: int = typer.Option(0, help="Minimale Anzahl CVEs für Filterung"),
    min_exploits: int = typer.Option(0, help="Minimale Anzahl Exploits für Filterung")
):
    """
    Extrahiert Komponenten-CVEs + Zusammenfassung aus EMBA HTML.
    Optional filterbar nach minimaler Anzahl an CVEs und Exploits.
    """
    from src.emba_parser import extract_cves_auto, assign_risk_level, plot_risk_level_distribution
    from src.file_writer import export_to_csv

    components_df, summary_df = extract_cves_auto(filepath)

    # 🔍 Filter anwenden
    filtered_df = components_df[
        (components_df["cves"] >= min_cves) &
        (components_df["exploits"] >= min_exploits)
    ]

    filtered_df = assign_risk_level(filtered_df)
    plot_risk_level_distribution(filtered_df)
    #print("\n🔸 Risikostufenverteilung:\n")

    print("🔹 Gefilterte Komponenten mit CVEs und Risikostufenverteilung:\n", filtered_df.head())
    #print("\n🔸 CVE-Zusammenfassung:\n", summary_df.to_string(index=False))

    if export:
        export_to_csv(filtered_df, export)
        


"""
@app.command()
def generate_emba_report(
    filepath: str = typer.Option(..., help="Pfad zur index.html oder f17_cve_bin_tool.html")
):
"""
    #Erstellt einen EMBA-spezifischen PDF-Report mit CVE-Charts und Zusammenfassung.
"""
    
    components_df, summary_df = extract_cves_auto(filepath)

    chart_path = "./charts/emba_top_cves.png"
    plot_top_cve_components(components_df, output_path=chart_path)
    export_emba_report_to_pdf(summary_df, chart_path)
"""

@app.command()
def generate_emba_report_full(
    filepath: str = typer.Option(..., help="Pfad zur EMBA index.html"),
):
    """
    Erstellt einen vollständigen PDF-Report mit Chart, CVE-Summary und Komponententabelle.

    """
    from src.emba_parser import extract_cves_auto, assign_risk_level, plot_top_cve_components, plot_risk_level_distribution
    from src.error_visualizer import export_emba_report_to_pdf
    
    components_df, summary_df = extract_cves_auto(filepath)
    components_df = assign_risk_level(components_df)

    plot_top_cve_components(components_df)
    plot_risk_level_distribution(components_df)

    chart_path = "./charts/emba_top_cves.png"
    pdf_path = "./charts/errors/emba_report_full.pdf"
    export_emba_report_to_pdf(summary_df, chart_path, components_df, pdf_path)

@app.command()
def zip_emba_report(
    basepath: str = typer.Option("./charts/errors", help="Verzeichnis mit EMBA-Reportdaten")
):
    """
    Packt PDF, Chart und ggf. CSV-Dateien des EMBA-Reports in ein ZIP.
    """
    from src.error_visualizer import export_emba_report_zip

    files = [
        os.path.join(basepath, "emba_report_full.pdf"),
        "./charts/emba_top_cves.png",
        "emba_components.csv",
        "emba_components_summary.csv"
    ]
    export_emba_report_zip(files)


@app.command()
def plot_emba_heatmap(
    filepath: str = typer.Option(..., help="Pfad zur EMBA index.html oder f17_cve_bin_tool.html")
):
    """
    Erstellt eine Heatmap der CVEs und Exploits pro Komponente.
    """
    from src.emba_parser import extract_cves_auto, plot_cve_heatmap

    components_df, _ = extract_cves_auto(filepath)
    plot_cve_heatmap(components_df)


import subprocess
import sys
import os

@app.command()
def gui_loganalyzer():
    """
    Startet die Streamlit GUI aus dem ./experimental/gui/ Verzeichnis
    """
    script_path = os.path.join("experimental", "gui", "gui_streamlit_loganalyzer_updated.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path], check=True)
    
@app.command()
def visualize_structured(filepath: str):
    """
    Visualisiert Fehlerzeitverlauf mit automatisch klassifizierten Fehlerarten (inkl. custom_regex).
    """
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        raise typer.Exit()

    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    df = parse_log_to_dataframe(text, classify=True)

    if df.empty:
        print("⚠️ Keine gültigen Logeinträge erkannt.")
        return

    console = Console()
    console.print(f"📊 Geladene Einträge: {len(df)}")
    console.print("🎨 Starte Zeitverlauf...")

    plot_error_timecourse(df)

    console.print("✅ Fertig.")



@app.command()
def compare_custom(directory: str = "./data"):
    """
    Vergleicht benutzerdefinierte Fehlerarten über alle Logdateien im Verzeichnis.
    """
    df = compare_custom_error_logs(directory)
    if df.empty:
        print("⚠️ Keine Fehlerdaten erkannt.")
        return
    
    
    print("📊 Vergleich der Fehlerarten pro Datei:")
    print(df.to_string(index=False))

    # Visualisierung als gruppierter Balkenplot
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="error_type", y="count", hue="filename")
    plt.title("Benutzerdefinierte Fehlerverteilung pro Logdatei")
    plt.xlabel("Fehlerart")
    plt.ylabel("Anzahl")
    plt.xticks(rotation=45)
    plt.tight_layout()

    os.makedirs("./charts/custom", exist_ok=True)
    outpath = "./charts/custom/error_comparison_custom.png"
    plt.savefig(outpath)
    plt.close()
    print(f"✅ Diagramm gespeichert unter: {outpath}")

    # Heatmap erzeugen
    pivot = df.pivot_table(index="filename", columns="error_type", values="count", fill_value=0)
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu")
    plt.title("Heatmap: Fehlerarten je Logdatei")
    plt.xlabel("Fehlerart")
    plt.ylabel("Logdatei")
    plt.tight_layout()
    heat_path = "./charts/custom/error_comparison_heatmap_custom.png"
    plt.savefig(heat_path)
    plt.close()
    print(f"✅ Heatmap gespeichert unter: {heat_path}")

    # PDF erstellen
    from fpdf import FPDF
    pdf_path = "./charts/custom/error_comparison_report.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Vergleichsbericht - Fehlerarten", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Automatisch generiert aus Loganalyse", ln=1)
    pdf.ln(5)

    for title, path in [("Balkenplot: Fehlerarten pro Datei", outpath), ("Heatmap: Fehlerarten je Logdatei", heat_path)]:
        if os.path.exists(path):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, title, ln=1)
            pdf.image(path, w=180)
            pdf.ln(5)

    pdf.output(pdf_path, "F")
    print(f"📄 PDF-Bericht gespeichert unter: {pdf_path}")


@app.command()
def show_log_summary(filepath: str):
    """
    Zeigt Zusammenfassung und vorgeschlagene Klassifikatoren aus einer Logdatei.
    """
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        raise typer.Exit()

    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    df = parse_log_to_dataframe(text, classify=False)

    if df.empty:
        print("⚠️ Keine Logzeilen erkannt.")
        raise typer.Exit()

    console = Console()
    console.print(f"\n📊 [bold]Anzahl erkannter Zeilen:[/] {len(df)}")

    if "suggested_classes" in df.attrs:
        console.print("\n🧠 [bold green]Vorgeschlagene Fehlergruppen basierend auf den häufigsten Nachrichtentypen:[/]")
        for k, v in df.attrs["suggested_classes"].items():
            console.print(f" • [cyan]{k}[/cyan] → [magenta]{v}x[/magenta]")
    else:
        print("(Keine Vorschläge verfügbar)")

@app.command()
def generate_custom_patterns(
    json_file: str = typer.Argument("./charts/streamlit_exports/suggested_classes.json"),
    output_file: str = typer.Argument("./src/custom_patterns_generated.py")
):
    from src.custom_pattern_loader import load_custom_patterns
    from src.generate_custom_pattern import generate_py_module
    from pathlib import Path
    """
    Generiert ein Python-Modul mit CUSTOM_PATTERNS aus einer suggested_classes.json-Datei.
    """
    json_path = Path(json_file)
    if not json_path.exists():
        print(f"❌ Datei nicht gefunden: {json_file}")
        raise typer.Exit(1)

    patterns = load_custom_patterns(json_path)
    generate_py_module(patterns, output_file)




if __name__ == "__main__":
    app()
