# src/file_reader.py – Datei einlesen

def read_text_file(path):
    """Liest eine Textdatei im UTF-8-Format und gibt den Inhalt als String zurück."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Datei nicht gefunden: {path}")
        return None
    except Exception as e:
        print(f"❌ Fehler beim Lesen der Datei {path}: {e}")
        return None
