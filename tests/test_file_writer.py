# tests/test_file_writer.py – Tests für Exportfunktionen

import os
import unittest
from src.file_writer import export_to_csv, export_to_json

class TestFileWriter(unittest.TestCase):

    def setUp(self):
        self.test_data = [
            {"filename": "test1.txt", "words": 10},
            {"filename": "test2.txt", "words": 20}
        ]
        self.csv_path = "test_output.csv"
        self.json_path = "test_output.json"

    def tearDown(self):
        for file in [self.csv_path, self.json_path]:
            if os.path.exists(file):
                os.remove(file)

    def test_export_csv_creates_file(self):
        export_to_csv(self.test_data, self.csv_path)
        self.assertTrue(os.path.exists(self.csv_path))

    def test_export_json_creates_file(self):
        export_to_json(self.test_data, self.json_path)
        self.assertTrue(os.path.exists(self.json_path))
