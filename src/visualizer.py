# src/visualizer.py (aufgeräumte Version, Stand: 30.04.2025)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_analysis(data, output_dir="./charts"):
    """Erstellt und speichert grundlegende Visualisierungen aus der Analyse."""
    summary_dir = os.path.join(output_dir, "summary")
    os.makedirs(summary_dir, exist_ok=True)

    df = pd.DataFrame(data)
    sns.set_theme(style="whitegrid")

    # Balkendiagramm: Anzahl Wörter pro Logdatei
    plt.figure(figsize=(8, 5))
    sns.barplot(x="filename", y="words", data=df, hue="filename", palette="viridis", legend=False)
    plt.xticks(rotation=45, ha="right")
    plt.title("Anzahl Wörter pro Logdatei")
    plt.tight_layout()
    plt.savefig(os.path.join(summary_dir, "words_per_logfile.png"))
    plt.close()

    # Histogramm: Verteilung der Zeichenanzahl
    plt.figure(figsize=(8, 5))
    sns.histplot(df["chars"], kde=True, color="skyblue")
    plt.title("Verteilung der Zeichenanzahl")
    plt.tight_layout()
    plt.savefig(os.path.join(summary_dir, "chars_distribution.png"))
    plt.close()

    print(f"✅ Zusammenfassende Charts gespeichert unter: {summary_dir}")

def plot_trends(data, output_dir="./charts"):
    """Erstellt Trend-Scatterplots zur Untersuchung von Zusammenhängen."""
    trends_dir = os.path.join(output_dir, "trends")
    os.makedirs(trends_dir, exist_ok=True)

    df = pd.DataFrame(data)
    sns.set_theme(style="whitegrid")

    # Scatterplot: Zeilen vs. Dateigröße
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x="lines", y="bytes", data=df, color="blue", s=100)
    plt.title("Zeilenanzahl vs. Dateigröße (Bytes)")
    plt.tight_layout()
    plt.savefig(os.path.join(trends_dir, "lines_vs_bytes.png"))
    plt.close()

    # Scatterplot: Wörter vs Zeichen
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x="words", y="chars", data=df, color="green", s=100)
    plt.title("Wörteranzahl vs. Zeichenanzahl")
    plt.tight_layout()
    plt.savefig(os.path.join(trends_dir, "words_vs_chars.png"))
    plt.close()

    print(f"✅ Trend-Charts gespeichert unter: {trends_dir}")

def plot_error_types(data, output_dir="./charts"):
    """Visualisiert die Verteilung der Fehlerarten pro Datei als gestapeltes Balkendiagramm."""
    # DataFrame aus der Fehleranalyse aufbauen
    df = pd.DataFrame(data)
    # Annahme: Jeder Eintrag in data hat Schlüssel 'filename' und je Fehlerart eine Zählung
    df = df.set_index('filename')

    # Relevante Fehlerklassen
    error_types = [
        'sensor_error',
        'voltage_warning',
        'communication_error',
        'firmware_issue',
        'collision_error'
    ]
    # Sicherstellen, dass alle Spalten vorhanden sind
    for et in error_types:
        if et not in df.columns:
            df[et] = 0
    
    # Ausgabeverzeichnis anlegen
    error_dir = os.path.join(output_dir, "errors")
    os.makedirs(error_dir, exist_ok=True)

    # Gestapeltes Balkendiagramm
    ax = df[error_types].plot(
        kind='bar',
        stacked=True,
        figsize=(12, 7)
    )
    plt.title("Fehlerart-Verteilung pro Datei")
    plt.xlabel("Dateiname")
    plt.ylabel("Anzahl Fehler")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Speichern und schließen
    output_path = os.path.join(error_dir, "error_types_stacked_bar.png")
    plt.savefig(output_path)
    plt.close()

    print(f"✅ Fehlerart-Chart gespeichert unter: {output_path}")


