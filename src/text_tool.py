# src/text_tool.py – Textoperationen

def remove_whitespace(text):
    """Entfernt doppelte und führende Leerzeichen aus einem Text."""
    return ' '.join(text.split())

def word_count(text):
    """Zählt die Wörter im übergebenen Text."""
    return len(text.split())
