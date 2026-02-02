import asyncio
import websockets
import json
import random
from bot.config import HOST, PORT
from bot.utils.logger import logger, packet_logger
from bot.logic.solver import WordSolver

# ========================================
# SERVIDOR WEBSOCKET DEL BOT
# ========================================
class BotServer:
    def __init__(self):
        self.solver = WordSolver()
        self.current_player_words = {}
        self.next_custom_phrase = None
        self.pending_events = []
        
        self.event_handlers = {
            "setup": self.on_setup,
            "nextTurn": self.on_next_turn,
            "failWord": self.on_fail_word,
            "correctWord": self.on_correct_word,
            "setMilestone": self.on_set_milestone,
            "configUpdate": self.on_config_update,
            "customMessage": self.on_custom_message,
            "setPlayerWord": self.on_set_player_word,
            "livesLost": self.on_info_event,
            "bonusAlphabetCompleted": self.on_info_event,
            "addPlayer": self.on_info_event,
            "removePlayer": self.on_info_event,
            "setRules": self.on_info_event,
        }

    # ========================================
    # GESTIÓN DE CONEXIONES
    # ========================================
    async def handle_connection(self, websocket):
        client_addr = websocket.remote_address
        logger.info(f"[CONN] Cliente conectado desde: {client_addr}")

        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[CONN] Cliente desconectado: {client_addr}")
        except Exception as e:
            logger.error(f"[ERROR] Error en la conexión: {e}")

    async def process_message(self, websocket, message):
        packet_logger.debug(f"[RECV] {message}")

        try:
            data = json.loads(message)
            if not isinstance(data, dict): return

            event_type = data.get("event")
            payload = data.get("data")

            if not isinstance(event_type, str): return

            handler = self.event_handlers.get(event_type)
            if handler:
                await handler(websocket, payload)

        except json.JSONDecodeError:
            logger.warning("[WARN] Mensaje recibido no es un JSON válido.")
        except Exception as e:
            logger.error(f"[ERROR] Error procesando mensaje: {e}")

    # ========================================
    # MANEJADORES DE EVENTOS DEL JUEGO
    # ========================================
    async def on_setup(self, websocket, payload):
        self.solver.set_my_id(payload.get("selfPeerId"))
        logger.info(f"[SETUP] Setup completo. Mi ID es: {self.solver.my_peer_id}")
        
        try:
            milestone = payload.get("milestone", {})
            dict_manifest = milestone.get("dictionaryManifest", {})
            language_name = dict_manifest.get("name", "Spanish")
            self.solver.set_language(language_name)
        except Exception as e:
            logger.error(f"[SETUP] Error detectando idioma: {e}. Usando español.")
            self.solver.set_language("Spanish")
        
        await self.send_initial_config(websocket)
        
        if self.pending_events:
            logger.info(f"[SETUP] Procesando {len(self.pending_events)} eventos pendientes...")
            for event_type, event_payload in self.pending_events:
                handler = self.event_handlers.get(event_type)
                if handler:
                    await handler(websocket, event_payload)
            self.pending_events.clear()

    async def on_next_turn(self, websocket, payload):
        if self.solver.my_peer_id is None:
            logger.info("[CACHE] Evento nextTurn recibido antes del setup. Guardando...")
            self.pending_events.append(("nextTurn", payload))
            return
        
        if isinstance(payload, list):
            player_id = payload[0]
            syllable = payload[1]
        else:
            player_id = payload.get("playerPeerId")
            syllable = payload.get("syllable")

        is_my_turn = (player_id == self.solver.my_peer_id)
        logger.info(f"[TURN] Turno de {player_id} (Yo: {self.solver.my_peer_id}) | Sílaba: '{syllable}'")

        if is_my_turn:
            self.last_syllable = syllable
            if not self.solver.is_active:
                logger.info("[PAUSE] Es mi turno, pero el bot está desactivado.")
                return
            await self.play_turn(websocket, syllable)

    async def on_fail_word(self, websocket, payload):
        if isinstance(payload, list):
            player_id, reason = payload[0], payload[1]
        else:
            player_id, reason = payload.get("playerPeerId"), payload.get("reason")

        if player_id == self.solver.my_peer_id:
            logger.warning(f"[FAIL] Fallé la palabra. Razón: {reason}")
            
            if reason == "notInDictionary" and hasattr(self, 'last_attempted_word'):
                bad_word = self.last_attempted_word
                logger.warning(f"[BAN] Baneando palabra inválida: {bad_word}")
                self.solver.ban_word(bad_word)
                
                if hasattr(self, 'last_syllable'):
                    if not self.solver.is_active:
                        return
                    logger.info("[RETRY] Reintentando con otra palabra...")
                    await self.play_turn(websocket, self.last_syllable)

    async def on_correct_word(self, websocket, payload):
        if self.solver.my_peer_id is None:
            logger.info("[CACHE] Evento correctWord recibido antes del setup. Guardando...")
            self.pending_events.append(("correctWord", payload))
            return
        
        player_id = payload.get("playerPeerId")
        
        if player_id == self.solver.my_peer_id:
            bonus_letters = payload.get("bonusLetters")
            if bonus_letters:
                self.solver.update_bonus_alphabet(bonus_letters)

        if player_id is not None:
            word = self.current_player_words.get(player_id)
            if word:
                self.solver.mark_word_as_used(word)
                self.solver.learn_word(word)

    async def on_set_player_word(self, websocket, payload):
        if isinstance(payload, list) and len(payload) >= 2:
            self.current_player_words[payload[0]] = payload[1]

    async def on_set_milestone(self, websocket, payload):
        if isinstance(payload, list) and len(payload) > 0: payload = payload[0]
        if not isinstance(payload, dict): return

        milestone_name = payload.get("name")
        logger.debug(f"[MILESTONE] Milestone: {milestone_name}")

        if milestone_name == "seating":
            dictionary_manifest = payload.get("dictionaryManifest", {})
            bonus_alphabet = dictionary_manifest.get("bonusAlphabet")
            if bonus_alphabet:
                self.solver.set_bonus_alphabet(bonus_alphabet)

            self.solver.reset_used_words()
            self.solver.save_dictionary()
            logger.info("[RESET] Vuelta a la sala de espera. Memoria reiniciada.")
            
            if self.solver.autojoin:
                logger.info("[AUTOJOIN] Auto-unirse activado.")
                await websocket.send(json.dumps({"action": "unirse_juego"}))

        elif milestone_name == "round":
            current_player = payload.get("currentPlayerPeerId")
            syllable = payload.get("syllable")
            
            if current_player == self.solver.my_peer_id:
                logger.info(f"[START] ¡Empiezo yo la ronda! Sílaba: '{syllable}'")
                self.last_syllable = syllable
                
                if self.solver.is_active:
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    await self.play_turn(websocket, syllable)

    async def on_config_update(self, websocket, payload):
        logger.info(f"[CONFIG] Configuración recibida: {payload}")
        self.solver.update_config(payload)

        if payload.get("autojoin") is True:
            logger.info("[AUTOJOIN] Autojoin activado manualmente.")
            await websocket.send(json.dumps({"action": "unirse_juego"}))

    async def on_custom_message(self, websocket, payload):
        if payload:
            self.next_custom_phrase = payload
            logger.info(f"[CHAT] Frase personalizada encolada: {payload}")

    async def on_info_event(self, websocket, payload):
        pass

    # ========================================
    # SINCRONIZACIÓN DE CONFIGURACIÓN
    # ========================================
    async def send_initial_config(self, websocket):
        """Envía la configuración inicial del servidor a Tampermonkey."""
        config = {
            "minTypingDelay": self.solver.min_typing_delay,
            "maxTypingDelay": self.solver.max_typing_delay,
            "startDelayMin": self.solver.start_delay_min,
            "startDelayMax": self.solver.start_delay_max,
            "active": self.solver.is_active,
            "autojoin": self.solver.autojoin,
            "suicide": self.solver.suicide,
        }
        
        msg = json.dumps({"event": "initialConfig", "data": config})
        await websocket.send(msg)
        logger.info(f"[CONFIG] Configuración inicial enviada a Tampermonkey")

    # ========================================
    # LÓGICA DE JUEGO
    # ========================================
    async def play_turn(self, websocket, syllable):
        if self.next_custom_phrase:
            logger.info(f"[CHAT] Enviando frase personalizada: {self.next_custom_phrase}")
            await self._type_text(websocket, self.next_custom_phrase)
            
            msg = json.dumps({"action": "escribir_palabra", "word": self.next_custom_phrase})
            packet_logger.debug(f"[SEND] (Custom Phrase): {msg}")
            await websocket.send(msg)
            self.next_custom_phrase = None
            
            await asyncio.sleep(0.5)
        
        if self.solver.suicide:
            logger.warning("[SUICIDE] Modo suicide activado. Enviando /suicide...")
            await self._type_text(websocket, "/suicide")
            
            msg = json.dumps({"action": "escribir_palabra", "word": "/suicide"})
            packet_logger.debug(f"[SEND] (Suicide): {msg}")
            await websocket.send(msg)
            return
        
        word = self.solver.solve(syllable)
        if not word:
            logger.warning(f"[FAIL] No encontré ninguna palabra con '{syllable}'")
            return

        self.last_attempted_word = word
        logger.info(f"[SOLVE] Solución encontrada: {word}")
        
        think_time = random.uniform(self.solver.start_delay_min, self.solver.start_delay_max)
        logger.info(f"[THINK] Pensando durante {think_time:.2f}s...")
        await asyncio.sleep(think_time)

        await self._type_text(websocket, word)

        msg = json.dumps({"action": "escribir_palabra", "word": word})
        packet_logger.debug(f"[SEND] (Submit): {msg}")
        await websocket.send(msg)

    async def _type_text(self, websocket, text):
        """Simula tecleo letra por letra."""
        current_text = ""
        for char in text:
            current_text += char
            await websocket.send(json.dumps({"action": "teclear_texto", "text": current_text}))
            await asyncio.sleep(random.uniform(self.solver.min_typing_delay, self.solver.max_typing_delay))

    # ========================================
    # INICIALIZACIÓN DEL SERVIDOR
    # ========================================
    async def start(self):
        logger.info(f"[INIT] Iniciando servidor en ws://{HOST}:{PORT}")
        async with websockets.serve(self.handle_connection, HOST, PORT):
            await asyncio.Future()
