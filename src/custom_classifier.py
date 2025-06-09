# custom_classifier.py – dynamische Fehlerklassifikation mit Regex

import re

# Erste einfache Implementierung von get_suggestions()

DEFAULT_SUGGESTIONS = {
    "sensor_error": ["sensor failed", "sensor error"],
    "voltage_warning": ["voltage drop", "low voltage"],
    "communication_error": ["timeout", "CAN-Bus timeout"],
    "firmware_issue": ["firmware exception", "assertion failed"],
    "collision_error": ["collision", "obstacle detected"]
}

def get_suggestions(logtext: str):
    log_lower = logtext.lower()
    found = set()
    results = []

    for category, patterns in DEFAULT_SUGGESTIONS.items():
        for pattern in patterns:
            if pattern.lower() in log_lower and pattern not in found:
                found.add(pattern)
                results.append({"pattern": pattern, "category": category})

    return results



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
    from custom_patterns_generated_old import CUSTOM_PATTERNS as GENERATED_PATTERNS
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
            #print(f"{message} → {label}")
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