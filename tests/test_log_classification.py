import unittest
from src.custom_classifier import classify_custom_error
from src.data_analysis import parse_log_to_dataframe

class TestLogClassification(unittest.TestCase):

    def test_classify_custom_error(self):
        tests = {
            "[ERROR] CAN-Bus timeout on channel 4": "can_bus_timeout",
            "Firmware exception at address 0x5C4F": "firmware_exception",
            "Voltage drop detected: 10.49V": "voltage_drop",
            "Sensor failed: ID 3": "sensor_failed",
            "Obstacle detected near waypoint 29": "obstacle_detected",
            "Something completely different": "generic_error",
        }
        for msg, expected in tests.items():
            with self.subTest(msg=msg):
                self.assertEqual(classify_custom_error(msg), expected)

    def test_parse_log_to_dataframe(self):
        log_text = """
        [2025-05-21 10:01:00] ERROR CAN-Bus timeout on channel 4
        [2025-05-21 10:02:00] ERROR Firmware exception at address 0x5C4F
        [2025-05-21 10:03:00] ERROR Obstacle detected near waypoint 29
        [2025-05-21 10:04:00] ERROR Sensor failed: ID 3
        [2025-05-21 10:05:00] ERROR Voltage drop detected: 10.49V"""
        df = parse_log_to_dataframe(log_text, classify=True)
        self.assertEqual(len(df), 5)
        self.assertIn("timestamp", df.columns)
        self.assertIn("error_type", df.columns)
        self.assertIn("message", df.columns)
        self.assertEqual(df["error_type"].iloc[0], "can_bus_timeout")

if __name__ == "__main__":
    unittest.main()
