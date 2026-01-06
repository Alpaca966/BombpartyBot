import os

# Configuración de Red
HOST = "localhost"
PORT = 8765

# Rutas de Archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Raíz del proyecto
DATA_DIR = os.path.join(BASE_DIR, "data")
DICT_DIR = os.path.join(DATA_DIR, "diccionarios")
DICT_PATH = os.path.join(DICT_DIR, "es.txt")  # Por defecto español (se actualiza dinámicamente)
LOG_FILE = os.path.join(BASE_DIR, "bot_server.log")
LOG_PACKETS_FILE = os.path.join(DATA_DIR, "packets.log")

# Configuración de Tiempos (Simulación Humana)
MIN_TYPING_DELAY = 0.05  # Segundos mínimos entre letras
MAX_TYPING_DELAY = 0.15  # Segundos máximos entre letras
START_DELAY_MIN = 0.5    # Tiempo mínimo para "pensar" antes de empezar a escribir
START_DELAY_MAX = 1.5    # Tiempo máximo para "pensar"


# Configuración del Juego
MIN_WORD_LENGTH = 0
MAX_WORD_LENGTH = 30
