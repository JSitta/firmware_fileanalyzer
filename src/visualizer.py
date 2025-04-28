# src/visualizer.py (überarbeitete Version)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_analysis(data, output_dir="./charts"):
    """Erstellt und speichert Visualisierungen aus der Analyse."""
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame(data)

    # Seaborn-Theme setzen
    sns.set_theme(style="whitegrid")

    # 1. Balkendiagramm: Wörter pro Datei
    plt.figure(figsize=(8, 5))
    # sns.barplot(x="filename", y="words", data=df, palette="viridis")
    sns.barplot(x="filename", y="words", data=df, hue="filename", palette="viridis", legend=False)
    plt.xticks(rotation=45, ha="right")
    plt.title("Wörter pro Datei")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "chart_words_per_file.png"))
    plt.close()

    # 2. Histogramm: Verteilung der Zeichen
    plt.figure(figsize=(8, 5))
    sns.histplot(df["chars"], kde=True, color="skyblue")
    plt.title("Verteilung der Zeichenanzahl")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "chart_chars_distribution.png"))
    plt.close()

    # 3. Scatterplot: Zeilen vs Dateigröße
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x="lines", y="bytes", data=df, color="coral", s=100)
    plt.title("Zeilen vs Dateigröße")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "chart_lines_vs_bytes.png"))
    plt.close()

    print(f"✅ Alle Charts gespeichert unter: {output_dir}")


# src/visualizer.py (überarbeitete Version)
def plot_trends(data, output_dir="./charts"):
    """Erstellt Scatterplots für einfache Trendanalyse."""
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame(data)
    sns.set_theme(style="whitegrid")

    # 1. Zeilen vs Dateigröße
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x="lines", y="bytes", data=df, color="blue", s=100)
    plt.title("Zeilenanzahl vs. Dateigröße (Bytes)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "trend_lines_vs_bytes.png"))
    plt.close()

    # 2. Wörter vs Zeichen
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x="words", y="chars", data=df, color="green", s=100)
    plt.title("Wörteranzahl vs. Zeichenanzahl")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "trend_words_vs_chars.png"))
    plt.close()

    print(f"✅ Trend-Charts gespeichert im Ordner: {output_dir}")

