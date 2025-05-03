import os
import zipfile
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime


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
    """
    df = df.copy()
    df["hour"] = df["timestamp"].dt.floor("h")
    grouped = df.groupby(["hour", "error_type"]).size().reset_index(name="count")
    critical = grouped[grouped["count"] >= threshold]
    return critical.sort_values(by=["hour", "error_type"])

def append_critical_summary_to_pdf(df: pd.DataFrame, pdf: FPDF, threshold: int = 5):
    """
    Fügt dem PDF eine Tabelle mit den kritischsten Fehlerzeiträumen hinzu.
    """
    critical_df = detect_critical_error_windows(df, threshold)
    if critical_df.empty:
        return

    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Kritische Fehlerzeiträume (ab Schwelle)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.cell(50, 10, "Stunde", border=1)
    pdf.cell(60, 10, "Fehlerart", border=1)
    pdf.cell(30, 10, "Anzahl", border=1, ln=True)

    for _, row in critical_df.iterrows():
        pdf.cell(50, 10, str(row["hour"]), border=1)
        pdf.cell(60, 10, row["error_type"], border=1)
        pdf.cell(30, 10, str(row["count"]), border=1, ln=True)



def export_error_report_to_pdf(df: pd.DataFrame, output_dir="./charts/errors"):
    """
    Erstellt ein einfaches PDF mit Deckblatt, Zusammenfassung und eingebetteten Fehlerplots.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Deckblatt
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(200, 20, txt="Fehleranalyse-Report", ln=True, align="C")
    pdf.set_font("Arial", size=14)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.cell(200, 10, txt="Projekt: Firmware File Analyzer", ln=True, align="C")
    pdf.ln(30)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=(
        "Dieser Bericht enthält eine visuelle Auswertung der im Log erkannten Fehlerarten.\n"
        "Enthalten sind:\n"
        "- Fehlerverteilung pro Stunde (gestapelt)\n"
        "- Fehlertrends über die Zeit (Linienverlauf)\n"
        "- Heatmap nach Fehlerart und Zeitintervall\n"
        "- Kritische Zeitfenster mit hoher Fehlerrate\n"
    ))

    # Geordnete Plots mit sinnvollen Titeln, hier kommen nur Bilddateien rein, die vierte Seite ist eine Tabelle
    # und wird weiter unten mit appen_critical_summary_to_pdf ergänzt
    plots = {
        "error_time_stacked_bar.png": "Fehleranzahl pro Stunde (gestapelt)",
        "error_time_lines.png": "Fehlertrends über die Zeit",
        "error_time_heatmap.png": "Heatmap: Fehlerarten über Stunden"
    }

    for image_file, title in plots.items():
        path = os.path.join(output_dir, image_file)
        if os.path.exists(path):
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, txt=title, ln=True)
            pdf.image(path, w=190)
            pdf.ln(10)

    # Kritische Zeiträume ergänzen
    append_critical_summary_to_pdf(df, pdf)

    report_path = os.path.join(output_dir, "fehlerreport.pdf")
    pdf.output(report_path)
    print(f"📄 PDF-Report gespeichert unter: {report_path}")


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
