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
    

    def report_pandas(self, export_path="report.csv"):
        """Zusätzliche Analyse mit pandas – statistisch & exportierbar"""
        try:
            import pandas as pd
        except ImportError:
            print("📦 Hinweis: pandas ist nicht installiert. Installiere es mit `pip install pandas`.")
            return

        if not self.file_stats:
            print("⚠️ Keine Dateistatistiken vorhanden.")
            return

        df = pd.DataFrame(self.file_stats)

        print("\n📊 Erweiterte Statistik (pandas):")
        print(df.describe(include='all').round(2))

        df.to_csv(export_path, index=False)
        print(f"💾 Exportiert nach: {export_path}")
        
        
        # Am Ende der Methode report_pandas(), öffnet automatisch die.CSV Datei in Windows mit der
        # Funktion Öffnen mit: Excel ist hier bei CSV-Dateien voreingestellt.
        try:
            os.startfile(export_path)
        except Exception as e:
            print(f"⚠️ Konnte Datei nicht automatisch öffnen: {e}")


# Hier kommt die TextAnalyzer-Klasse hinein.
