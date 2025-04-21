# src/log_util.py – Logging-Konfiguration

import logging

def setup_logger():
    """Konfiguriert das Logging für das Projekt."""
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
