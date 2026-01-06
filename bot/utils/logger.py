import logging
import sys
from typing import Literal
from bot.config import LOG_FILE, LOG_PACKETS_FILE, LOG_LEVEL

# ========================================
# FORMATEADOR CON COLORES ANSI
# ========================================
class ColoredFormatter(logging.Formatter):
    """Formateador personalizado con colores ANSI para terminal."""
    
    GREY = "\x1b[38;5;240m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    BOLD_RED = "\x1b[31;1m"
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    RESET = "\x1b[0m"

    FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

    FORMATS = {
        logging.DEBUG: GREY + FORMAT + RESET,
        logging.INFO: GREEN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }

    def __init__(self, fmt=None, datefmt=None, style: Literal['%', '{', '$'] = '%'):
        if fmt is None:
            fmt = self.FORMAT
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        msg = record.msg
        if isinstance(msg, str):
            if "[CHAT]" in msg:
                return self.CYAN + super().format(record) + self.RESET
            if "[SOLVE]" in msg:
                return self.BLUE + super().format(record) + self.RESET
        
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

# ========================================
# CONFIGURACIÓN DE LOGGERS
# ========================================
def setup_logger():
    """Configura el logger principal de la aplicación."""
    
    logger = logging.getLogger("JKLM_Bot")
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    if logger.handlers:
        return logger

    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(datefmt='%H:%M:%S'))
    logger.addHandler(console_handler)

    return logger

def setup_packet_logger():
    """Configura logger específico para tráfico de red."""
    packet_logger = logging.getLogger("JKLM_Packets")
    packet_logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
    
    if packet_logger.handlers:
        return packet_logger

    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')
    
    file_handler = logging.FileHandler(LOG_PACKETS_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    packet_logger.addHandler(file_handler)
    
    packet_logger.propagate = False 
    
    return packet_logger

# ========================================
# INSTANCIAS GLOBALES
# ========================================
logger = setup_logger()
packet_logger = setup_packet_logger()
