import logging
import os
from datetime import datetime

from config import BASE_DIR

# Crear carpeta de logs si no existe
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

logger = logging.getLogger()
if not logger.handlers:
    logger.setLevel(logging.INFO)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(logs_dir, f"selenium_log_{timestamp}.log")
    
    # Crear handler para archivo
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    # Crear handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Silenciar loggers de terceros que sean muy verbosos
    for noisy_logger in ["WDM", "urllib3", "selenium"]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

# Exportar variables si es necesario
LOG_FILE = log_file if 'log_file' in locals() else None
TIMESTAMP = timestamp if 'timestamp' in locals() else None