# main.py – Einstiegspunkt

import argparse
import logging
from src.text_tool import remove_whitespace, word_count
from src.log_util import setup_logger
from src.text_analyzer import TextAnalyzer

setup_logger()

def main():
    parser = argparse.ArgumentParser(description="Textanalyse-Tool")
    parser.add_argument('--dir', type=str, default="./data", help='Verzeichnis mit .txt-Dateien')
    args = parser.parse_args()

    analyzer = TextAnalyzer(args.dir)
    if analyzer.collect_files():
        analyzer.analyze()
        analyzer.report()

        # Beispiel Textoperation
        example_text = "   Das   ist    ein   Test.   "
        cleaned = remove_whitespace(example_text)
        print(f"Bereinigter Text: '{cleaned}'")
        print(f"Wortanzahl: {word_count(cleaned)}")
        logging.info("Textoperation durchgeführt: remove_whitespace + word_count")

if __name__ == '__main__':
    main()
