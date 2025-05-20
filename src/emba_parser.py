from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import matplotlib.pyplot as plt 
import seaborn as sns
from typing import Optional # Optional für Typannotationen


# Neue Funktion zur Deployment-Entscheidung basierend auf typischen Grenzwerten
def evaluate_firmware_acceptance(log_df: pd.DataFrame) -> tuple[bool, str]:
    """
    Bewertet auf Basis der Fehlerarten, ob eine Firmware für das Deployment geeignet ist.
    Gibt zurück: (True/False, Begründung)
    """
    if log_df.empty or "error_type" not in log_df.columns:
        return True, "Kein Fehlerprotokoll erkannt – Deployment möglich."

    counts = log_df["error_type"].value_counts().to_dict()
    firmware_issues = counts.get("firmware_issue", 0)
    voltage_issues = counts.get("voltage_warning", 0)
    sensor_errors = counts.get("sensor_error", 0)

    if firmware_issues >= 2:
        return False, f"Firmware enthält {firmware_issues} kritische firmware_issue-Fehler."
    if voltage_issues >= 3:
        return False, f"Mehr als {voltage_issues} Spannungseinbrüche erkannt."
    if sensor_errors >= 3:
        return False, f"Mehr als {sensor_errors} Sensorausfälle festgestellt."

    return True, "✅ Firmwarefreigabe möglich – keine kritischen Fehler detektiert."


def extract_summary_from_index(filepath: str) -> pd.DataFrame:
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    entries = []
    collect = False
    lines = []

    for pre in soup.find_all("pre"):
        line = pre.get_text(strip=True)

        # Startbedingung flexibler gestalten (beginnt mit "identified ... cve")
        if re.search(r"identified.*cve entries", line, re.IGNORECASE):
            collect = True

        if collect:
            lines.append(line)

        # Endbedingung: letzte Zeile enthält "verified exploits"
        if collect and re.search(r"verified exploits", line, re.IGNORECASE):
            break

    for entry in lines:
        entries.append({"summary": entry})

    return pd.DataFrame(entries)


# Unverändert: extract_cves_from_f17 und extract_cves_auto

def extract_cves_from_f17(filepath: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    components = []
    summary = []

    comp_pattern = re.compile(
        r"component details:\s*(?P<component>[\w\-\.]+)\s*:\s*(?P<version>[^:]+?)\s*:\s*cves:\s*(?P<cves>\d+)\s*:\s*exploits:\s*(?P<exploits>\d+)",
        re.IGNORECASE
    )
    for pre in soup.find_all("pre"):
        text = pre.get_text()
        match = comp_pattern.search(text)
        if match:
            components.append({
                "component": match.group("component"),
                "version": match.group("version"),
                "cves": int(match.group("cves")),
                "exploits": int(match.group("exploits"))
            })

    collect = False
    lines = []
    for pre in soup.find_all("pre"):
        line = pre.get_text(strip=True)
        if re.search(r"identified.*cve entries", line, re.IGNORECASE):
            collect = True
        if collect:
            lines.append(line)
        if collect and re.search(r"verified exploits", line, re.IGNORECASE):
            break

    for entry in lines:
        summary.append({"summary": entry})

    return pd.DataFrame(components), pd.DataFrame(summary)


def extract_cves_auto(filepath: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if re.search(r"component\s+details", content, re.IGNORECASE):
        return extract_cves_from_f17(filepath)
    else:
        dummy = pd.DataFrame(columns=["component", "version", "cves", "exploits"])
        return dummy, extract_summary_from_index(filepath)


def plot_top_cve_components(components_df: pd.DataFrame, output_path: str = "./charts/emba_top_cves.png"):
    """
    Erstellt ein Balkendiagramm der Top 10 Komponenten mit den meisten CVEs.
    """
    if components_df.empty or "cves" not in components_df.columns:
        print("⚠️ Keine CVE-Daten verfügbar für Chart.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    top = components_df.sort_values("cves", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top, x="cves", y="component", hue="component", palette="Reds_r", legend=False)
    plt.title("Top 10 Komponenten mit CVEs")
    plt.xlabel("Anzahl CVEs")
    plt.ylabel("Komponente")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"✅ Chart gespeichert unter: {output_path}")

def plot_cve_heatmap(components_df: pd.DataFrame, output_path: str = "./charts/emba_cve_heatmap.png"):
    """
    Erstellt eine Heatmap für CVEs und Exploits pro Komponente.
    """
    if components_df.empty:
        print("⚠️ Keine CVE-Daten für Heatmap verfügbar.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Optional: Top 20 Komponenten nach CVEs
    top = components_df.sort_values("cves", ascending=False).head(20)
    pivot = top.set_index("component")[["cves", "exploits"]]

    plt.figure(figsize=(10, max(6, len(pivot) * 0.4)))
    sns.heatmap(pivot, annot=True, cmap="YlOrRd", fmt="d", linewidths=0.5, cbar_kws={"label": "Anzahl"})
    plt.title("Heatmap: CVEs und Exploits pro Komponente")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"✅ CVE-Heatmap gespeichert unter: {output_path}")

def assign_risk_level(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bewertet CVE-Risiken für jede Komponente auf Basis einfacher Regeln.
    Fügt Spalten 'risk_score' und 'risk_level' hinzu.
    """
    def compute_score(row):
        score = 0
        if row["cves"] >= 10:
            score += 2
        if row["cves"] >= 50:
            score += 3
        if row["exploits"] >= 1:
            score += 2
        if row["exploits"] >= 5:
            score += 1
        if row["component"].lower() == "linux_kernel":
            score += 3
        return score

    def map_level(score):
        if score >= 7:
            return "kritisch"
        elif score >= 5:
            return "hoch"
        elif score >= 3:
            return "mittel"
        else:
            return "niedrig"

    df = df.copy()
    df["risk_score"] = df.apply(compute_score, axis=1)
    df["risk_level"] = df["risk_score"].apply(map_level)
    return df

def plot_cve_heatmap(components_df: pd.DataFrame, output_path: str = "./charts/emba_cve_heatmap.png"):
    if components_df.empty:
        print("⚠️ Keine CVE-Daten für Heatmap verfügbar.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    top = components_df.sort_values("cves", ascending=False).head(20)
    pivot = top.set_index("component")[["cves", "exploits"]]

    plt.figure(figsize=(10, max(6, len(pivot) * 0.4)))
    sns.heatmap(pivot, annot=True, cmap="YlOrRd", fmt="d", linewidths=0.5, cbar_kws={"label": "Anzahl"})
    plt.title("Heatmap: CVEs und Exploits pro Komponente")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"✅ CVE-Heatmap gespeichert unter: {output_path}")

def plot_risk_level_distribution(components_df: pd.DataFrame, output_path: str = "./charts/emba_risk_distribution.png"):
    """
    Erstellt ein Balkendiagramm zur Verteilung der Risikostufen.
    """
    if components_df.empty or "risk_level" not in components_df.columns:
        print("⚠️ Keine Risiko-Daten verfügbar für Verteilung.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    counts = components_df["risk_level"].value_counts().reindex(["kritisch", "hoch", "mittel", "niedrig"], fill_value=0)

    plt.figure(figsize=(8, 5))
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette="Reds", legend=False)
    plt.title("Verteilung der Schwachstellenrisiken")
    plt.xlabel("Risikostufe")
    plt.ylabel("Anzahl Komponenten")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"✅ Risiko-Verteilung gespeichert unter: {output_path}")

def append_risk_summary_table(pdf, components_df: pd.DataFrame):
    """
    Fügt eine gruppierte Risiko-Zusammenfassung in Tabellenform in das PDF ein.
    """
    if components_df.empty or "risk_level" not in components_df.columns:
        return

    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Risiko-Zusammenfassung nach Stufen", ln=1)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Risikostufe", border=1, align="L")
    pdf.cell(40, 8, "Anzahl Komponenten", border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", size=10)
    risk_counts = components_df["risk_level"].value_counts().reindex(["kritisch", "hoch", "mittel", "niedrig"], fill_value=0)
    for level, count in risk_counts.items():
        pdf.cell(60, 8, level.capitalize(), border=1, align="L")
        pdf.cell(40, 8, str(count), border=1, align="C")
        pdf.ln()

    pdf.ln(5)

def generate_risk_explanation(row) -> str:
    """
    Erzeugt eine erklärende Einschätzung auf Basis lokaler Regeln.
    """
    
    icons = { "kritisch": "[KRITISCH]", "hoch": "[HOCH]", "mittel": "[MITTEL]", "niedrig": "[OK]" }
    icon = icons.get(row.get("risk_level", "niedrig"), "")
    
    explanation = f"{icon} Komponente '{row['component']}' (v{row['version']}) weist {row['cves']} CVEs und {row['exploits']} bekannte Exploits auf. "
    if row['risk_level'] == "kritisch":
        explanation += "Aufgrund der sehr hohen CVE-Zahl, Exploit-Verfügbarkeit und Systemrelevanz wird sie als KRITISCH eingestuft."
    elif row['risk_level'] == "hoch":
        explanation += "Sie besitzt ein hohes Gefährdungspotenzial durch CVEs oder Exploits, ist aber weniger zentral als Kernel-Komponenten."
    elif row['risk_level'] == "mittel":
        explanation += "Die Komponente hat moderate Verwundbarkeit, aber keine akute Ausnutzbarkeit."
    else:
        explanation += "Die Risiken gelten aktuell als gering."
    return explanation

def append_risk_explanations_sorted(pdf, components_df: pd.DataFrame):
    """
    Fügt erklärende Risikobewertungen gruppiert nach Risikostufen in das PDF ein.
    """
    relevant = components_df[components_df["risk_score"] >= 3]  # nur ab mittlerem Risiko
    if relevant.empty:
        return

    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Erklärungen zu Schwachstellen (ab Risikostufe mittel)", ln=1)
    pdf.set_font("Arial", size=10)

    # Sortiert nach risk_level und dann nach risk_score (kritisch zuerst)
    order = {"kritisch": 0, "hoch": 1, "mittel": 2, "niedrig": 3}
    sorted_df = relevant.copy()
    sorted_df["_level_order"] = sorted_df["risk_level"].map(order)
    sorted_df = sorted_df.sort_values(by=["_level_order", "risk_score"], ascending=[True, False])

    for _, row in sorted_df.iterrows():
        text = generate_risk_explanation(row)
        pdf.multi_cell(0, 6, text, border=0)
        pdf.ln(2)




