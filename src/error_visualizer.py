import os
import zipfile
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime
from src.error_timeparser import build_error_dataframe


def plot_error_timecourse(df, output_dir="./charts"):
    """
    Visualisiert Fehlerhäufigkeit über die Zeit aus einem DataFrame mit 'timestamp' und 'error_type'.
    """
    time_dir = os.path.join(output_dir, "errors")
    os.makedirs(time_dir, exist_ok=True)

    df["hour"] = df["timestamp"].dt.floor("h")
    grouped = df.groupby(["hour", "error_type"]).size().unstack(fill_value=0)

    farben = {
        "sensor_error": "orange",
        "voltage_warning": "red",
        "communication_error": "blue",
        "firmware_issue": "purple",
        "collision_error": "green",
        "generic_error": "gray",
    }
    colorlist = [farben[col] for col in grouped.columns if col in farben]

    # Gestapelter Balkenplot
    ax1 = grouped.plot(kind="bar", stacked=True, figsize=(14, 6), color=colorlist)
    plt.title("Fehleranzahl pro Stunde (gestapelt)")
    plt.ylabel("Anzahl Fehler")
    plt.xlabel("Zeit (Stunde)")
    plt.xticks(rotation=45)
    plt.legend(title="Fehlerart", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    barpath = os.path.join(time_dir, "error_time_stacked_bar.png")
    plt.savefig(barpath)
    plt.close()

    # Linienplot
    ax2 = grouped.plot(kind="line", marker="o", figsize=(14, 6), color=colorlist)
    plt.title("Fehlertrends über die Zeit")
    plt.ylabel("Anzahl Fehler")
    plt.xlabel("Zeit (Stunde)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend(title="Fehlerart", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    linepath = os.path.join(time_dir, "error_time_lines.png")
    plt.savefig(linepath)
    plt.close()

    print(f"✅ Zeitverlauf-Charts gespeichert unter: {time_dir}")
    return barpath, linepath


def plot_error_heatmap(df, output_dir="./charts"):
    """
    Erstellt eine Heatmap der Fehlerarten über Stunden hinweg.
    """
    heatmap_dir = os.path.join(output_dir, "errors")
    os.makedirs(heatmap_dir, exist_ok=True)

    df["hour"] = df["timestamp"].dt.floor("h")
    heatmap_data = df.groupby(["error_type", "hour"]).size().unstack(fill_value=0)

    plt.figure(figsize=(14, 6))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlOrRd", linewidths=0.5, cbar_kws={"label": "Fehleranzahl"})
    plt.title("Heatmap: Fehlerarten über Zeit")
    plt.xlabel("Zeit (Stunde)")
    plt.ylabel("Fehlerart")
    plt.tight_layout()
    heatpath = os.path.join(heatmap_dir, "error_time_heatmap.png")
    plt.savefig(heatpath)
    plt.close()

    print(f"✅ Heatmap gespeichert unter: {os.path.join(heatmap_dir, 'error_time_heatmap.png')}")
    return heatpath

def detect_critical_error_windows(df: pd.DataFrame, threshold: int = 5) -> pd.DataFrame:
    """
    Gibt alle Stunden + Fehlerarten zurück, bei denen die Fehleranzahl >= threshold ist.
    Erwartet ein DataFrame mit Timestamp.
    """
    if "timestamp" not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df["hour"] = df["timestamp"].dt.floor("h")
    grouped = df.groupby(["hour", "error_type"]).size().reset_index(name="count")
    critical = grouped[grouped["count"] >= threshold]
    return critical.sort_values(by=["hour", "error_type"])


def append_critical_summary_to_pdf(df: pd.DataFrame, pdf: FPDF, threshold: int = 5):
    critical_df = detect_critical_error_windows(df, threshold)
    if critical_df.empty:
        return
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Kritische Fehlerzeiträume", ln=1)
    pdf.set_font("Arial", size=10)
    for _, row in critical_df.iterrows():
        line = f"{row['hour']} - {row['error_type']} - {row['count']}x"
        pdf.cell(0, 10, line, ln=1)


def export_error_report_to_pdf(df: pd.DataFrame, output_dir="./charts/errors"):
    os.makedirs(output_dir, exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Fehleranalyse-Report", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1)
    pdf.ln(10)

    # Geordnete Plots mit sinnvollen Titeln
    plots = {
        "error_time_stacked_bar.png": "Fehleranzahl pro Stunde (gestapelt)",
        "error_time_lines.png": "Fehlertrends über die Zeit",
        "error_time_heatmap.png": "Heatmap: Fehlerarten über Stunden",
        "error_comparison_barplot.png": "Vergleich: Fehleranzahl je Logdatei",
        "error_comparison_heatmap.png": "Vergleich: Heatmap je Logdatei"
    }
    for image_file, title in plots.items():
        path = os.path.join(output_dir, image_file)
        if os.path.exists(path):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, title, ln=1)
            pdf.image(path, w=180)
            pdf.ln(10)

    # Kritische Zeiträume ergänzen (nur wenn Zeitstempel vorhanden)
    append_critical_summary_to_pdf(df, pdf)

    report_path = os.path.join(output_dir, "fehlerreport.pdf")
    pdf.output(report_path)
    print(f"✅ PDF-Report exportiert: {report_path}")


def export_report_as_zip(output_dir: str = "./charts/errors", zip_name: str = "error_report_bundle.zip"):
    """
    Erstellt ein ZIP-Archiv aller relevanten Exportdateien im Reportverzeichnis.
    """
    zip_path = os.path.join(output_dir, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in [
            "fehlerreport.pdf",
            "error_time_stacked_bar.png",
            "error_time_lines.png",
            "error_time_heatmap.png"
        ]:
            path = os.path.join(output_dir, filename)
            if os.path.exists(path):
                zipf.write(path, arcname=filename)
    print(f"📦 ZIP-Archiv erstellt: {zip_path}")


def publish_reports_to_docs(source_dir: str = "./charts/errors", target_dir: str = "./docs/reports"):
    """
    Kopiert alle Reportdateien aus dem Quellverzeichnis in ein öffentliches docs-Verzeichnis.
    """
    os.makedirs(target_dir, exist_ok=True)
    exported_files = []
    for filename in os.listdir(source_dir):
        if filename.endswith(('.pdf', '.png', '.svg', '.zip')):
            src = os.path.join(source_dir, filename)
            dst = os.path.join(target_dir, filename)
            shutil.copy2(src, dst)
            exported_files.append(dst)
    print(f"📁 Veröffentlichte Dateien:")
    for path in exported_files:
        print(f" → {path}")


def compare_error_logs(directory: str) -> pd.DataFrame:
    """
    Vergleicht Fehlerarten über mehrere Logdateien in einem Verzeichnis.
    Gibt eine Tabelle mit error_type, count und Dateiname zurück.
    """
    summary = []

    for fname in os.listdir(directory):
        if fname.endswith(".txt"):
            fpath = os.path.join(directory, fname)
            with open(fpath, encoding="utf-8") as f:
                lines = f.readlines()
            df = build_error_dataframe(lines)

            if df.empty or "error_type" not in df.columns:
                print(f"⚠️ Datei übersprungen (ungültig oder leer): {fname}")
                continue

            df = df[df["error_type"] != "info"]
            counts = df["error_type"].value_counts().reset_index()
            counts.columns = ["error_type", "count"]
            counts["filename"] = fname
            summary.append(counts)

    if not summary:
        return pd.DataFrame(columns=["filename", "error_type", "count"])

    return pd.concat(summary, ignore_index=True)[["filename", "error_type", "count"]]


def plot_error_comparison(df: pd.DataFrame, output_dir="./charts"):
    """
    Erstellt einen gruppierten Balkenplot zur Fehlerverteilung über mehrere Logdateien.
    """
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="error_type", y="count", hue="filename")
    plt.title("Fehlerverteilung pro Logdatei")
    plt.xlabel("Fehlerart")
    plt.ylabel("Anzahl")
    plt.xticks(rotation=45)
    plt.tight_layout()
    out_path = os.path.join(output_dir, "error_comparison_barplot.png")
    plt.savefig(out_path)
    plt.close()
    print(f"✅ Vergleichsdiagramm gespeichert unter: {out_path}")


def plot_error_heatmap_logs(df: pd.DataFrame, output_dir="./charts"):
    """
    Erstellt eine Heatmap der Fehlerarten pro Logdatei.
    """
    os.makedirs(output_dir, exist_ok=True)
    pivot = df.pivot_table(index="filename", columns="error_type", values="count", fill_value=0)
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="OrRd", fmt=".0f")
    plt.title("Heatmap: Fehlerarten je Logdatei")
    plt.xlabel("Fehlerart")
    plt.ylabel("Logdatei")
    plt.tight_layout()
    out_path = os.path.join(output_dir, "error_comparison_heatmap.png")
    plt.savefig(out_path)
    plt.close()
    print(f"✅ Heatmap gespeichert unter: {out_path}")

