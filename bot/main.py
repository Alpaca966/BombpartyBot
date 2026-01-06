import asyncio
import sys
import os

# Asegurar que el directorio raíz está en el path para las importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.network.server import BotServer
from bot.utils.logger import logger

def main():
    logger.info("[INIT] JKLM Bot - Iniciando sistema...")
    
    server = BotServer()
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("\n[STOP] Servidor detenido por el usuario.")
        server.solver.save_dictionary()
    except Exception as e:
        logger.critical(f"[CRITICAL] Error fatal en el sistema: {e}")
        server.solver.save_dictionary()

if __name__ == "__main__":
    main()
