# Modul: TextAnalyzer
# src/text_analyzer.py – zentrale Analyseklasse
# src/text_analyzer.py – zentrale Analyseklasse (erweitert mit Statistik)

import os
import logging
from src.file_reader import read_text_file
from src.text_tool import word_count

class TextAnalyzer:
    def __init__(self, directory):
        self.directory = directory
        self.txt_files = []
        self.file_stats = []
        self.total_lines = 0
        self.total_words = 0
        self.total_chars = 0
        self.total_bytes = 0
        self.largest_file_lines = ''
        self.largest_file_words = ''

    def collect_files(self):
        if not os.path.isdir(self.directory):
            logging.error(f"❌ Verzeichnis nicht gefunden: {self.directory}")
            return False
        self.txt_files = [f for f in os.listdir(self.directory) if f.endswith('.txt')]
        if not self.txt_files:
            logging.warning(f"⚠️ Keine .txt-Dateien gefunden in: {self.directory}")
            return False
        return True

    def analyze(self):
        max_lines = 0
        max_words = 0
        for filename in self.txt_files:
            path = os.path.join(self.directory, filename)
            text = read_text_file(path)
            if text:
                lines = text.count('\n') + 1
                words = word_count(text)
                chars = len(text)
                bytesize = os.path.getsize(path)

                self.total_lines += lines
                self.total_words += words
                self.total_chars += chars
                self.total_bytes += bytesize

                self.file_stats.append({
                    "filename": filename,
                    "lines": lines,
                    "words": words,
                    "chars": chars,
                    "bytes": bytesize
                })

                if lines > max_lines:
                    max_lines = lines
                    self.largest_file_lines = filename
                if words > max_words:
                    max_words = words
                    self.largest_file_words = filename

        logging.info(
            "Analyse durchgeführt für %d Dateien. Zeilen: %d, Wörter: %d, Zeichen: %d, Bytes: %d",
            len(self.txt_files), self.total_lines, self.total_words, self.total_chars, self.total_bytes
        )

    def report(self):
        print("📊 Analyseergebnisse:")
        print(f"Anzahl .txt-Dateien: {len(self.txt_files)}")
        print(f"Gesamtanzahl Zeilen: {self.total_lines}")
        print(f"Gesamtanzahl Wörter: {self.total_words}")
        print(f"Gesamtanzahl Zeichen: {self.total_chars}")
        print(f"Gesamtanzahl Dateigröße (Bytes): {self.total_bytes}")
        print(f"Größte Datei (Zeilen): {self.largest_file_lines}")
        print(f"Größte Datei (Wörter): {self.largest_file_words}")

        if self.file_stats:
            avg_lines = self.total_lines / len(self.file_stats)
            avg_words = self.total_words / len(self.file_stats)
            avg_chars = self.total_chars / len(self.file_stats)
            avg_bytes = self.total_bytes / len(self.file_stats)

            print("\n📈 Durchschnitt pro Datei:")
            print(f"- Zeilen: {avg_lines:.2f}")
            print(f"- Wörter: {avg_words:.2f}")
            print(f"- Zeichen: {avg_chars:.2f}")
            print(f"- Bytes: {avg_bytes:.2f}")

# Ergänzung mit pandas - python analysis data system -   
    
    def report_pandas(self, export_path="report.csv", file_format="csv"):
        """Erweiterte Statistik mit pandas – als CSV oder JSON, inkl. Filter & Diagramm"""
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
        except ImportError:
            print("📦 Hinweis: pandas oder matplotlib ist nicht installiert.")
            print("👉 Installiere sie mit `pip install pandas matplotlib`.")
            return

        if not self.file_stats:
            print("⚠️ Keine Dateistatistiken vorhanden.")
            return

        df = pd.DataFrame(self.file_stats)

        print("\n📊 Erweiterte Statistik (pandas):")
        print(df.describe(include='all').round(2))

        # 🔍 Top 3 Dateien nach Wortanzahl
        print("\n📄 Top 3 Dateien mit den meisten Wörtern:")
        top_words = df.sort_values("words", ascending=False).head(3)
        print(top_words[["filename", "words"]].to_string(index=False))

        # 📈 Diagramm anzeigen
        try:
            plt.figure(figsize=(8, 4))
            df_sorted = df.sort_values("words", ascending=False)
            plt.bar(df_sorted["filename"], df_sorted["words"], color='skyblue')
            plt.title("Wörter pro Datei")
            plt.ylabel("Anzahl Wörter")
            plt.xlabel("Dateiname")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"⚠️ Konnte Diagramm nicht anzeigen: {e}")

        # 💾 Exportieren
        try:
            if file_format.lower() == "json":
                df.to_json(export_path, orient="records", indent=2)
            else:
                df.to_csv(export_path, index=False)

            print(f"💾 Exportiert nach: {export_path}")
            try:
                os.startfile(export_path)
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ Export oder Öffnen fehlgeschlagen: {e}")


# Hier kommt die TextAnalyzer-Klasse hinein.
