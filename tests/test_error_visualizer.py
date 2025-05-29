import shutil
import sys
import os
import zipfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import unittest
import pandas as pd
from datetime import datetime
from error_visualizer import (detect_critical_error_windows, export_error_report_to_pdf,
                              export_report_as_zip, publish_reports_to_docs)

class TestErrorVisualizer(unittest.TestCase):

    def setUp(self):
        # Beispiel-Daten vorbereiten
        self.data = pd.DataFrame({
            "timestamp": [
                datetime(2025, 5, 1, 10, 0),
                datetime(2025, 5, 1, 10, 15),
                datetime(2025, 5, 1, 10, 30),
                datetime(2025, 5, 1, 10, 45),
                datetime(2025, 5, 1, 10, 50),
                datetime(2025, 5, 1, 11, 5)
            ],
            "error_type": [
                "sensor_error",
                "sensor_error",
                "sensor_error",
                "sensor_error",
                "firmware_issue",
                "sensor_error"
            ]
        })

    def test_detect_threshold(self):
        result = detect_critical_error_windows(self.data, threshold=4)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["error_type"], "sensor_error")
        self.assertEqual(result.iloc[0]["count"], 4)

class TestPDFExport(unittest.TestCase):

    def setUp(self):
        self.test_dir = "./charts/test_export"
        os.makedirs(self.test_dir, exist_ok=True)
        self.df = pd.DataFrame({
            "timestamp": [
                datetime(2025, 5, 1, 10, 0),
                datetime(2025, 5, 1, 10, 15),
                datetime(2025, 5, 1, 11, 0)
            ],
            "error_type": [
                "sensor_error",
                "sensor_error",
                "firmware_issue"
            ]
        })

    def test_pdf_created(self):
        pdf_path = os.path.join(self.test_dir, "test_report.pdf")
        export_error_report_to_pdf(self.df, output_path=pdf_path)
        self.assertTrue(os.path.isfile(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 1000)  # rudimentäre Prüfung auf „echten Inhalt“

    def tearDown(self):
        shutil.rmtree(self.test_dir)

class TestZIPExport(unittest.TestCase):

    def setUp(self):
        self.test_dir = "./charts/test_zip"
        os.makedirs(self.test_dir, exist_ok=True)
        # Dummy-Dateien anlegen
        with open(os.path.join(self.test_dir, "fehlerreport.pdf"), "w") as f:
            f.write("Dummy PDF")
        with open(os.path.join(self.test_dir, "error_time_lines.png"), "w") as f:
            f.write("Dummy PNG")
        with open(os.path.join(self.test_dir, "error_time_stacked_bar.png"), "w") as f:
            f.write("Dummy Bar")
        with open(os.path.join(self.test_dir, "error_time_heatmap.png"), "w") as f:
            f.write("Dummy Heatmap")

    def test_zip_created(self):
        export_report_as_zip(output_dir=self.test_dir, zip_name="test_bundle.zip")
        zip_path = os.path.join(self.test_dir, "test_bundle.zip")
        self.assertTrue(os.path.isfile(zip_path))

        with zipfile.ZipFile(zip_path, "r") as zipf:
            contents = zipf.namelist()
            self.assertIn("fehlerreport.pdf", contents)
            self.assertIn("error_time_lines.png", contents)
            self.assertIn("error_time_stacked_bar.png", contents)
            self.assertIn("error_time_heatmap.png", contents)

    def tearDown(self):
        shutil.rmtree(self.test_dir)


class TestDocsPublisher(unittest.TestCase):

    def setUp(self):
        self.source = "./charts/test_publish"
        self.target = "./docs/reports_test"
        os.makedirs(self.source, exist_ok=True)
        # Dummy-Dateien mit gültigen Endungen
        for fname in [
            "fehlerreport.pdf",
            "error_time_lines.png",
            "error_time_stacked_bar.png",
            "error_time_heatmap.png",
            "error_report_bundle.zip"
        ]:
            with open(os.path.join(self.source, fname), "w") as f:
                f.write("Dummy content")

    def test_files_published(self):
        publish_reports_to_docs(source_dir=self.source, target_dir=self.target)
        for fname in [
            "fehlerreport.pdf",
            "error_time_lines.png",
            "error_time_stacked_bar.png",
            "error_time_heatmap.png",
            "error_report_bundle.zip"
        ]:
            self.assertTrue(os.path.exists(os.path.join(self.target, fname)))

    def tearDown(self):
        shutil.rmtree(self.source)
        shutil.rmtree(self.target)
