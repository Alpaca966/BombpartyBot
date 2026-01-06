import os
from dotenv import load_dotenv

load_dotenv()

# ========================================
# CONFIGURACIÓN DE RED
# ========================================
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "8765"))

# ========================================
# RUTAS DEL SISTEMA
# ========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
DICT_DIR = os.path.join(DATA_DIR, "diccionarios")

DICT_PATH = os.path.join(DICT_DIR, "es.txt")
LOG_FILE = os.path.join(LOGS_DIR, "bot_server.log")
LOG_PACKETS_FILE = os.path.join(LOGS_DIR, "packets.log")

# ========================================
# SIMULACIÓN DE COMPORTAMIENTO HUMANO
# ========================================
MIN_TYPING_DELAY = float(os.getenv("MIN_TYPING_DELAY", "0.05"))
MAX_TYPING_DELAY = float(os.getenv("MAX_TYPING_DELAY", "0.15"))
START_DELAY_MIN = float(os.getenv("START_DELAY_MIN", "0.5"))
START_DELAY_MAX = float(os.getenv("START_DELAY_MAX", "1.5"))

# ========================================
# CONFIGURACIÓN DE LOGGING
# ========================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
