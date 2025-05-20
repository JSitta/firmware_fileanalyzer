import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.error_timeparser import build_error_dataframe
from src.emba_parser import evaluate_firmware_acceptance
from src.error_visualizer import export_error_report_to_pdf
import os
import time
import signal

# Streamlit GUI für die Firmware-Analyse
# Importiere die notwendigen Module

st.set_page_config(page_title="Firmware File Analyzer", layout="wide")
st.title("🛠️ Firmware File Analyzer")


st.markdown("""
Willkommen zur grafischen Oberfläche! Lade eine Logdatei hoch und analysiere automatisch,
ob die Firmware für den Produktionseinsatz geeignet ist.
""")

uploaded_file = st.file_uploader("📂 Wähle eine Logdatei (.txt)", type=["txt"])

if uploaded_file is not None:
    # Zeilen einlesen und verarbeiten
    lines = uploaded_file.read().decode("utf-8").splitlines()
    df = build_error_dataframe(lines)

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

    st.markdown("### 📄 PDF-Export")
    import datetime

    # 📄 Automatischer Standardname basierend auf Upload-Name oder Zeit
    default_name = uploaded_file.name.replace(".txt", "_report.pdf") if uploaded_file.name else f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    default_path = os.path.join("./charts/errors", default_name)
    export_path = st.text_input("📁 Speicherpfad für PDF:", value=default_path)

    # 📄 PDF-Export über Button
    if st.button("📄 PDF-Report erzeugen"):
        if export_path and export_path.lower().endswith(".pdf"):
            export_error_report_to_pdf(df, output_path = export_path)
            st.success(f"PDF-Report gespeichert unter: {export_path}")
            st.markdown(f"[🔗 Öffnen]({export_path})")
            st.session_state["export_path"] = export_path  # optional speichern
        else:
            st.warning("Bitte gib einen gültigen Pfad für den PDF-Export an.")

    if st.button("🔁 Neue Datei analysieren"):
        st.rerun()

    else:
            st.warning("Bitte gib einen gültigen Pfad für den PDF-Export an.")

else:
        st.info("Bitte wähle eine Datei aus.")

# Beenden-Button unten auf der Seite
st.markdown("---")
if st.button("🚪 Beenden und schließen"):
    st.success("✅ Anwendung beendet. Du kannst das Fenster nun schließen oder mit einer neuen Datei starten.")
    st.markdown("Du kannst das Fenster jetzt schließen.")
   # st.stop()

    time.sleep(2)
    os.kill(os.getpid(), signal.SIGTERM)
