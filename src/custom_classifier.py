# custom_classifier.py – dynamische Fehlerklassifikation mit Regex

import re

# Basis-CUSTOM_PATTERNS – manuell gepflegt oder Standard
CUSTOM_PATTERNS = {
    "can_bus_timeout": r"can\s*-?bus\s+timeout\s+on\s+channel",
    "firmware_exception": r"firmware\s+exception\s+at\s+address",
    "obstacle_detected": r"obstacle\s+detected\s+near\s+waypoint",
    "voltage_drop": r"voltage\s+drop\s+detected",
    "sensor_failed": r"sensor\s+failed",
    "generic_error": r".*",
}
#print("✅ CUSTOM_PATTERNS geladen:", CUSTOM_PATTERNS)
# Optional: automatisch generierte Patterns ergänzen
try:
    from src.custom_patterns_generated import CUSTOM_PATTERNS as GENERATED_PATTERNS
    CUSTOM_PATTERNS.update(GENERATED_PATTERNS)
except ImportError:
    print("⚠️ Keine automatisch generierten CUSTOM_PATTERNS gefunden.")

def classify_custom_error(message: str) -> str:
    """
    Klassifiziert eine Fehlermeldung anhand definierter Regex-Muster.
    Gibt den Klassennamen zurück oder 'generic_error'.
    """
    for label, pattern in CUSTOM_PATTERNS.items():
        if re.search(pattern, message, re.IGNORECASE):
            print(f"{message} → {label}")
            return label
    return "generic_error"

"""
# Beispielanwendung (optional):
if __name__ == "__main__":
    tests = [
        "[ERROR] CAN-Bus timeout on channel 4",
        "Firmware exception at address 0x5C4F",
        "Voltage drop detected: 10.49V",
        "Sensor failed: ID 3",
        "Obstacle detected near waypoint 29",
        "Unclassified message"
    ]

    for line in tests:
        result = classify_custom_error(line)
        print(f"{line} → {result}")
"""