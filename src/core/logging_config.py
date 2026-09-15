import logging
from pathlib import Path

# 1. Definir la ruta raíz del proyecto y la carpeta de logs
# __file__ es este archivo -> src/core/logging_config.py
# .parents[2] sube 2 niveles hasta la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]
LOGS_DIR = BASE_DIR / "logs"

# 2. Crear la carpeta logs/ si no existe
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 3. Ruta absoluta al archivo de log
LOG_FILE_PATH = LOGS_DIR / "app.log"

# 4. Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("app_logger")