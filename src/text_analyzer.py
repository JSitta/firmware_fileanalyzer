# Modul: TextAnalyzer
# src/text_analyzer.py – zentrale Analyseklasse

import os
import logging
from src.file_reader import read_text_file
from src.text_tool import word_count

class TextAnalyzer:
    def __init__(self, directory):
        self.directory = directory
        self.txt_files = []
        self.total_lines = 0
        self.total_words = 0
        self.total_chars = 0
        self.total_bytes = 0
        self.largest_file_lines = ''
        self.largest_file_words = ''

    #def collect_files(self):
    #    if not os.path.isdir(self.directory):
    #        logging.error(f"❌ Verzeichnis nicht gefunden: {self.directory}")
    #        return False
    #    self.txt_files = [
    #        os.path.join(self.directory, f)
    #        for f in os.listdir(self.directory)
    #        if f.endswith('.txt')
    #    ]
    #    if not self.txt_files:
    #        logging.warning(f"⚠️ Keine .txt-Dateien gefunden in: {self.directory}")
    #        return False
    #    return True
    
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

# Hier kommt die TextAnalyzer-Klasse hinein.
