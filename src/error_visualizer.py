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


def export_error_report_to_pdf(df: pd.DataFrame, output_path: str = "./charts/errors/fehlerreport.pdf" ):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
    output_dir = os.path.dirname(output_path)
    for image_file, title in plots.items():
        path = os.path.join(output_dir, image_file)
        if os.path.exists(path):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, title, ln=1)
            pdf.image(path, w=180)
            pdf.ln(10)

    # Kritische Zeiträume ergänzen (nur wenn Zeitstempel vorhanden)
    append_critical_summary_to_pdf(df, pdf)

    
    pdf.output(output_path)
    print(f"✅ PDF-Report exportiert: {output_path}")


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

def export_emba_report_to_pdf(summary_df, chart_path, components_df=None, output_path="./charts/errors/emba_report_full.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    from src.emba_parser import append_risk_summary_table, generate_risk_explanation, append_risk_explanations_sorted
    # PDF-Report erstellen

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "EMBA Sicherheitsauswertung", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1)
    pdf.ln(5)

    # CVE-Zusammenfassung
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "CVE-Zusammenfassung", ln=1)
    pdf.set_font("Arial", size=10)
    for _, row in summary_df.iterrows():
        pdf.cell(0, 8, row["summary"], ln=1)

    # Chart einbinden
    if os.path.exists(chart_path):
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Top 10 CVE-Komponenten", ln=1)
        pdf.image(chart_path, w=180)

    # Komponententabelle
    if components_df is not None and not components_df.empty:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Komponententabelle mit Risikobewertung", ln=1)
        pdf.set_font("Arial", "B", 9)

        # Spaltenüberschriften
        col_widths = [48, 28, 18, 20, 25]  # in mm
        headers = ["Komponente", "Version", "CVEs", "Exploits", "Risikostufe"]

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, align="L")
        pdf.ln()

        pdf.set_font("Arial", size=9)
        for _, row in components_df.iterrows():
            values = [
                str(row["component"])[:32],
                str(row["version"]),
                str(row["cves"]),
                str(row["exploits"]),
                str(row["risk_level"])
            ]
            for i, val in enumerate(values):
                pdf.cell(col_widths[i], 6, val, border=1, align="L")
            pdf.ln()

    # Nach der Tabelle oder auf neuer Seite:
    append_risk_summary_table(pdf, components_df)
    
    # Risikobewertung, Regelbasierte Erklärung

    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Lokale Risikoanalyse kritischer Komponenten", ln=1)
    pdf.set_font("Arial", size=10)

    for _, row in components_df[components_df["risk_score"] >= 7].iterrows():
        text = generate_risk_explanation(row)
        pdf.multi_cell(0, 6, text, border=0)
        pdf.ln(2)

    # Am Ende vor pdf.output(...) einfügen:
    risk_chart = "./charts/emba_risk_distribution.png"
    if os.path.exists(risk_chart):
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Verteilung der Risikostufen", ln=1)
        pdf.image(risk_chart, w=180)
        pdf.ln(10)

    append_risk_explanations_sorted(pdf, components_df)

    pdf.output(output_path)
    print(f"📄 PDF-Report gespeichert unter: {output_path}")

def export_emba_report_zip(
    files: list[str],
    output_zip: str = "./charts/errors/emba_report_bundle.zip"
):
    os.makedirs(os.path.dirname(output_zip), exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fpath in files:
            if os.path.exists(fpath):
                arcname = os.path.basename(fpath)
                zipf.write(fpath, arcname=arcname)
                print(f"📎 Hinzugefügt: {arcname}")
            else:
                print(f"⚠️ Datei nicht gefunden und übersprungen: {fpath}")

    print(f"📦 ZIP-Archiv erstellt: {output_zip}")

