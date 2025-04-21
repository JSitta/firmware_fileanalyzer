# tests/test_text_analyzer.py – Testsuite für TextAnalyzer

import unittest
import os
from src.text_analyzer import TextAnalyzer

class TestTextAnalyzer(unittest.TestCase):

    def test_empty_directory(self):
        os.makedirs("temp_empty", exist_ok=True)
        analyzer = TextAnalyzer("temp_empty")
        self.assertFalse(analyzer.collect_files())
        os.rmdir("temp_empty")

    def test_sample_file_analysis(self):
        test_path = "test_sample.txt"
        content = "Ein kurzer Testtext."
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(content)

        analyzer = TextAnalyzer(".")
        analyzer.txt_files = [test_path]
        analyzer.analyze()

        self.assertGreaterEqual(analyzer.total_words, 3)
        self.assertEqual(analyzer.total_chars, len(content))
        self.assertEqual(analyzer.total_bytes, os.path.getsize(test_path))

        os.remove(test_path)

    def test_report_executes(self):
        test_path = "test_report.txt"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("Beispielinhalt für Reporting-Test.")

        analyzer = TextAnalyzer(".")
        analyzer.txt_files = [test_path]
        analyzer.analyze()

        try:
            analyzer.report()
        except Exception:
            self.fail("report() löste eine Ausnahme aus")

        os.remove(test_path)


