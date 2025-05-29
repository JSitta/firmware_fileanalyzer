from src.custom_pattern_loader import load_custom_patterns
from pathlib import Path

def generate_py_module(patterns: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# AUTO-GENERATED FILE – custom_patterns_generated.py\n")
        f.write("# Dieser Code wurde automatisch aus suggested_classes.json erzeugt.\n\n")
        f.write("CUSTOM_PATTERNS = {\n")
        for label, regex in patterns.items():
            regex = regex.replace("\\\\", "\\")  # Doppelte Backslashes entfernen
            f.write(f'    "{label}": r"{regex}",\n')
        f.write("}\n")
        print(f"✅ Generiert: {output_path}")