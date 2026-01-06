import logging
import sys
from typing import Literal
from bot.config import LOG_FILE, LOG_PACKETS_FILE

class ColoredFormatter(logging.Formatter):
    """Formatter personalizado para añadir colores ANSI en la consola."""
    
    # Códigos ANSI
    GREY = "\x1b[38;5;240m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    BOLD_RED = "\x1b[31;1m"
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    RESET = "\x1b[0m"

    # Formato base
    FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

    # Mapeo de niveles a colores
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
        # Personalización extra para nuestros tags específicos si están en el mensaje
        msg = record.msg
        if isinstance(msg, str):
            if "[CHAT]" in msg:
                # Usamos el formato base pero envuelto en CYAN
                return self.CYAN + super().format(record) + self.RESET
            if "[SOLVE]" in msg:
                # Usamos el formato base pero envuelto en BLUE
                return self.BLUE + super().format(record) + self.RESET
        
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

def setup_logger():
    """Configura y devuelve el logger principal de la aplicación."""
    
    # Crear logger
    logger = logging.getLogger("JKLM_Bot")
    logger.setLevel(logging.INFO)
    
    # Evitar duplicados si se llama varias veces
    if logger.handlers:
        return logger

    # Formato para archivo (sin colores)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

    # Handler de Archivo (UTF-8)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler de Consola (Con colores)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(datefmt='%H:%M:%S'))
    logger.addHandler(console_handler)

    return logger

def setup_packet_logger():
    """Configura un logger específico para el tráfico de paquetes."""
    packet_logger = logging.getLogger("JKLM_Packets")
    packet_logger.setLevel(logging.DEBUG)
    
    if packet_logger.handlers:
        return packet_logger

    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')
    
    # Archivo separado para paquetes
    file_handler = logging.FileHandler(LOG_PACKETS_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    packet_logger.addHandler(file_handler)
    
    # No agregamos console_handler para no saturar la terminal
    packet_logger.propagate = False 
    
    return packet_logger

# Instancia global para importar fácilmente
logger = setup_logger()
packet_logger = setup_packet_logger()
