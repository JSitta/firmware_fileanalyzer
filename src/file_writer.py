# src/file_writer.py – Textdatei schreiben

def write_text_file(path, text):
    """Speichert einen Text im UTF-8-Format an einem bestimmten Pfad."""
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(text)
            print(f"✅ Datei erfolgreich gespeichert: {path}")
    except Exception as e:
        print(f"❌ Fehler beim Schreiben in die Datei {path}: {e}")
        