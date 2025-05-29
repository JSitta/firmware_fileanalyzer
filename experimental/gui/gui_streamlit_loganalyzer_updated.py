import sys
from pathlib import Path    

# Dynamisch sicherstellen, dass 'src' importierbar ist
ROOT = Path(__file__).resolve().parent.parent.parent  # geht hoch bis zum Projektstamm (../..)
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data_analysis import parse_log_to_dataframe
from src.emba_parser import evaluate_firmware_acceptance
from src.error_visualizer import export_error_report_to_pdf
import os
import time

# Streamlit GUI für die Firmware-Analyse
st.set_page_config(page_title="Firmware File Analyzer", layout="wide")
st.title("🛠️ Firmware File Analyzer")

st.markdown("""
Willkommen zur grafischen Oberfläche! Lade eine Logdatei hoch und analysiere automatisch,
ob die Firmware für den Produktionseinsatz geeignet ist.
""")

uploaded_file = st.file_uploader("📂 Wähle eine Logdatei (.txt)", type=["txt"])

if uploaded_file is not None:
    # Zeilen einlesen und analysieren
    lines = uploaded_file.read().decode("utf-8").splitlines()
    text = "\n".join(lines)
    df = parse_log_to_dataframe(text, classify=True)
    # optional Vorschläge nachträglich ergänzen
    from src.data_analysis import parse_log_to_dataframe as parse_df_alt
    df_temp = parse_df_alt(text, classify=False)
    if hasattr(df_temp, "attrs") and "suggested_classes" in df_temp.attrs:
        df.attrs["suggested_classes"] = df_temp.attrs["suggested_classes"]

    st.markdown("### 🧪 Fehlerarten-Zeitverlauf")
    st.dataframe(df)

    st.markdown("### 📋 Deployment-Entscheidung")
    status, reason = evaluate_firmware_acceptance(df)

    if status:
        st.success(reason)
    else:
        st.error(reason)

    st.markdown("---")
    st.markdown(f"Anzahl Fehler insgesamt: **{len(df)}**")
    st.markdown(f"Verteilung nach Typ:")
    st.dataframe(df["error_type"].value_counts().reset_index().rename(columns={"index": "Fehlertyp", "error_type": "Anzahl"}))

    st.markdown("### 📊 Fehlerarten (Diagramm)")
    fig, ax = plt.subplots()
    df["error_type"].value_counts().plot(kind="bar", color="tomato", ax=ax)
    ax.set_ylabel("Anzahl")
    ax.set_xlabel("Fehlertyp")
    ax.set_title("Verteilung der Fehlerarten")
    st.pyplot(fig)

    st.markdown("### 📈 Fehlerzeitverlauf & Heatmap")
    df_hourly = df.copy()
    df_hourly["hour"] = df_hourly["timestamp"].dt.floor("h")
    grouped = df_hourly.groupby(["hour", "error_type"]).size().unstack(fill_value=0)

    # Gestapelter Zeitverlauf
    st.markdown("#### Fehleranzahl pro Stunde (gestapelt)")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    grouped.plot(kind="bar", stacked=True, ax=ax1)
    ax1.set_xlabel("Zeit (Stunde)")
    ax1.set_ylabel("Fehleranzahl")
    ax1.set_title("Gestapelte Fehler über Zeit")
    st.pyplot(fig1)

    # Heatmap
    st.markdown("#### Fehler-Heatmap")
    import seaborn as sns
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    sns.heatmap(grouped.T, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax2, cbar_kws={"label": "Fehleranzahl"})
    ax2.set_xlabel("Zeit (Stunde)")
    ax2.set_ylabel("Fehlerart")
    ax2.set_title("Heatmap: Fehlerarten über Zeit")
    st.pyplot(fig2)

    # 🧠 Exportbuttons für Charts + Vorschläge
    from src.error_visualizer import export_suggested_classes

    st.markdown("### 💾 Exportoptionen")
    export_chart_dir = "./charts/streamlit_exports"
    os.makedirs(export_chart_dir, exist_ok=True)

    if st.button("💾 Charts als PNG speichern"):
        fig1.savefig(os.path.join(export_chart_dir, "error_stacked_bar.png"))
        fig2.savefig(os.path.join(export_chart_dir, "error_heatmap.png"))
        st.success(f"Gespeichert in {export_chart_dir}")

    if hasattr(df, "attrs") and "suggested_classes" in df.attrs:
        if st.button("💾 suggested_classes.json exportieren"):
            json_path = os.path.join(export_chart_dir, "suggested_classes.json")
            export_suggested_classes(df, json_path)
            st.success(f"Vorschläge gespeichert unter: {json_path}")

    st.markdown("### 📄 PDF-Export")
    import datetime

    default_name = uploaded_file.name.replace(".txt", "_report.pdf") if uploaded_file.name else f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    default_path = os.path.join("./charts/errors", default_name)
    export_path = st.text_input("📁 Speicherpfad für PDF:", value=default_path)

    if st.button("📄 PDF-Report erzeugen"):
        if export_path and export_path.lower().endswith(".pdf"):
            export_error_report_to_pdf(df, output_path=export_path)
            st.success(f"PDF-Report gespeichert unter: {export_path}")
            st.markdown(f"[🔗 Öffnen]({export_path})")
            st.session_state["export_path"] = export_path
        else:
            st.warning("Bitte gib einen gültigen Pfad für den PDF-Export an.")

    if st.button("🔁 Neue Datei analysieren"):
        st.rerun()

else:
    st.info("Bitte wähle eine Datei aus.")

st.markdown("---")
if st.button("🚪 Beenden und schließen"):
    st.success("✅ Anwendung beendet. Du kannst das Fenster nun schließen.")
    st.stop()
