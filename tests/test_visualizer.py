import os
import unittest
import tempfile
from src.visualizer import plot_error_types, plot_analysis, plot_trends


class TestVisualizer(unittest.TestCase):
    def test_plot_error_types_creates_chart(self):
        data = [
            {"filename": "file1.txt", "sensor_error": 2, "voltage_warning": 1, "communication_error": 0, "firmware_issue": 3, "collision_error": 0},
            {"filename": "file2.txt", "sensor_error": 0, "voltage_warning": 2, "communication_error": 1, "firmware_issue": 0, "collision_error": 4},
        ]
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_dir = os.path.join(tmpdirname, "charts")
            plot_error_types(data, output_dir=output_dir)
            error_dir = os.path.join(output_dir, "errors")
            chart_path = os.path.join(error_dir, "error_types_stacked_bar.png")
            self.assertTrue(os.path.isdir(error_dir))
            self.assertTrue(os.path.isfile(chart_path))
            self.assertGreater(os.path.getsize(chart_path), 0)

    def test_plot_analysis_creates_summary_dir(self):
        data = [
            {"filename": "log1.txt", "lines": 100, "words": 500, "chars": 3000, "bytes": 2048, "errors": 12, "warnings": 5, "infos": 20},
            {"filename": "log2.txt", "lines": 80,  "words": 400, "chars": 2800, "bytes": 1980, "errors": 3,  "warnings": 7, "infos": 15},
        ]
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_dir = os.path.join(tmpdirname, "charts")
            plot_analysis(data, output_dir=output_dir)
            summary_dir = os.path.join(output_dir, "summary")
            self.assertTrue(os.path.isdir(summary_dir))
            self.assertGreater(len(os.listdir(summary_dir)), 0)

    def test_plot_trends_creates_trend_charts(self):
        data = [
            {"filename": "log1.txt", "lines": 100, "words": 500, "chars": 3000, "bytes": 2048},
            {"filename": "log2.txt", "lines": 80,  "words": 400, "chars": 2800, "bytes": 1980},
        ]
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_dir = os.path.join(tmpdirname, "charts")
            plot_trends(data, output_dir=output_dir)
            trends_dir = os.path.join(output_dir, "trends")
            self.assertTrue(os.path.isdir(trends_dir))
            self.assertGreater(len(os.listdir(trends_dir)), 0)


if __name__ == '__main__':
    unittest.main()
