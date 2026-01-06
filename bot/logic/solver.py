import os
import random
import re
from bot.config import DICT_DIR, MIN_TYPING_DELAY, MAX_TYPING_DELAY, START_DELAY_MIN, START_DELAY_MAX
from bot.utils.logger import logger

class WordSolver:
    # Mapeo de idiomas del juego a archivos de diccionario
    LANGUAGE_MAP = {
        "Spanish": "es.txt",
        "English": "en.txt",
        "German": "de.txt",
        "French": "fr.txt",
        "Italian": "it.txt",
        "Portuguese": "pt.txt",
    }
    
    def __init__(self):
        self.words = []
        self.used_words = set()
        self.my_peer_id = None
        self.current_language = None
        self.dict_path = None
        
        # Configuración
        self.is_active = True
        self.strategy = "random"
        self.autojoin = False
        self.suicide = False
        
        # Tiempos
        self.min_typing_delay = MIN_TYPING_DELAY
        self.max_typing_delay = MAX_TYPING_DELAY
        self.start_delay_min = START_DELAY_MIN
        self.start_delay_max = START_DELAY_MAX
        
        # Buffers para persistencia
        self.banned_words_buffer = set()
        self.new_words_buffer = set()
        self.bonus_alphabet = {}

    def set_my_id(self, peer_id):
        self.my_peer_id = peer_id
    
    def set_language(self, language_name):
        """Establece el idioma del juego y carga el diccionario correspondiente."""
        if language_name == self.current_language:
            return  # Ya está cargado
        
        dict_file = self.LANGUAGE_MAP.get(language_name)
        if not dict_file:
            logger.warning(f"[LANG] Idioma '{language_name}' no soportado. Usando español por defecto.")
            dict_file = "es.txt"
            language_name = "Spanish"
        
        self.current_language = language_name
        self.dict_path = os.path.join(DICT_DIR, dict_file)
        
        # Limpiar buffers al cambiar de idioma
        self.banned_words_buffer.clear()
        self.new_words_buffer.clear()
        
        self.load_dictionary()
        logger.info(f"[LANG] Idioma establecido: {language_name} ({dict_file})")

    def load_dictionary(self):
        """Carga el diccionario desde el archivo especificado en dict_path."""
        if not self.dict_path:
            logger.warning("[LOAD] No se ha establecido un diccionario. Esperando setup...")
            return
        
        try:
            with open(self.dict_path, "r", encoding="utf-8") as f:
                self.words = [line.strip().lower() for line in f if line.strip()]
            logger.info(f"[LOAD] Diccionario cargado: {len(self.words)} palabras.")
        except FileNotFoundError:
            logger.error(f"[ERROR] Diccionario no encontrado: {self.dict_path}")
            self.words = []
        except Exception as e:
            logger.error(f"[ERROR] Error cargando diccionario: {e}")
            self.words = []

    def set_bonus_alphabet(self, alphabet_dict):
        self.bonus_alphabet = alphabet_dict.copy()
        logger.info(f"[BONUS] Alfabeto bonus actualizado: {self.bonus_alphabet}")
        if self.strategy == "alphabet":
            self._log_alphabet_progress()

    def update_bonus_alphabet(self, updates_dict):
        self.bonus_alphabet.update(updates_dict)
        if self.strategy == "alphabet":
            self._log_alphabet_progress()
    
    def _log_alphabet_progress(self):
        """Muestra el progreso del alfabeto bonus cuando la estrategia está activa."""
        if not self.bonus_alphabet:
            return
        
        pending = [(letter, count) for letter, count in sorted(self.bonus_alphabet.items()) if count > 0]
        total_pending = sum(count for _, count in pending)
        
        if total_pending == 0:
            logger.info("[ALPHABET] ✓ ¡Alfabeto completado!")
        else:
            pending_letters = ', '.join([f"{letter}:{count}" for letter, count in pending])
            logger.info(f"[ALPHABET] Pendientes: {total_pending} letras → [{pending_letters}]")

    def reset_used_words(self):
        self.used_words.clear()

    def _normalize_word(self, word):
        """Elimina caracteres no válidos y espacios. Soporta español e inglés."""
        # Permitir letras comunes en español e inglés
        return re.sub(r'[^a-záéíóúüñ]', '', word.lower().strip())

    def mark_word_as_used(self, word):
        word = self._normalize_word(word)
        if word: self.used_words.add(word)

    def ban_word(self, word):
        if word in self.words:
            self.words.remove(word)
            self.banned_words_buffer.add(word)
            logger.warning(f"[BAN] Palabra baneada: {word}")

    def learn_word(self, word):
        word = self._normalize_word(word)
        if word and word not in self.words and word not in self.banned_words_buffer:
            self.words.append(word)
            self.new_words_buffer.add(word)
            logger.info(f"[LEARN] Palabra aprendida: {word}")

    def save_dictionary(self):
        if not self.dict_path:
            logger.warning("[SAVE] No se puede guardar: diccionario no establecido.")
            return
        
        if not self.banned_words_buffer and not self.new_words_buffer: 
            return

        logger.info(f"[SAVE] Guardando diccionario ({self.current_language})... (+{len(self.new_words_buffer)}, -{len(self.banned_words_buffer)})")
        
        try:
            with open(self.dict_path, "r", encoding="utf-8") as f:
                current_words = set(line.strip().lower() for line in f if line.strip())
            
            current_words -= self.banned_words_buffer
            current_words.update(self.new_words_buffer)
            
            with open(self.dict_path, "w", encoding="utf-8") as f:
                f.write("\n".join(sorted(current_words)))
            
            logger.info("[SAVE] Diccionario guardado.")
            self.banned_words_buffer.clear()
            self.new_words_buffer.clear()
            
        except Exception as e:
            logger.error(f"[ERROR] Error guardando diccionario: {e}")

    def update_config(self, config):
        if "active" in config: self.is_active = config["active"]
        if "autojoin" in config: self.autojoin = config["autojoin"]
        if "suicide" in config: self.suicide = config["suicide"]

        # Estrategias
        if config.get("strategy_alphabet"):
            self.strategy = "alphabet"
            self._log_alphabet_progress()  # Mostrar progreso al activar
        elif config.get("strategy_longest"): self.strategy = "longest"
        elif config.get("strategy_shortest"): self.strategy = "shortest"
        elif any(k in config for k in ["strategy_alphabet", "strategy_longest", "strategy_shortest"]):
            # Si se desactivó la actual y no hay otra, volver a random
            self.strategy = "random"

        # Tiempos
        if "minTypingDelay" in config: self.min_typing_delay = float(config["minTypingDelay"])
        if "maxTypingDelay" in config: self.max_typing_delay = float(config["maxTypingDelay"])
        if "startDelayMin" in config: self.start_delay_min = float(config["startDelayMin"])
        if "startDelayMax" in config: self.start_delay_max = float(config["startDelayMax"])

    def solve(self, syllable):
        syllable = syllable.lower()
        
        # Filtrado inicial
        candidates = [w for w in self.words if syllable in w and w not in self.used_words]
        
        # Optimización para modo random: limitar candidatos si hay muchos
        if self.strategy == "random" and len(candidates) > 50:
            candidates = candidates[:50]

        if not candidates:
            # Fallback: buscar en usadas
            return next((w for w in self.words if syllable in w), None)

        # Selección
        if self.strategy == "longest":
            choice = max(candidates, key=len)
        elif self.strategy == "shortest":
            choice = min(candidates, key=len)
        elif self.strategy == "alphabet":
            # Priorizar palabras que aporten más letras nuevas al bonus
            def score(w):
                return (sum(1 for c in set(w) if self.bonus_alphabet.get(c, 0) > 0), len(w))
            choice = max(candidates, key=score)
            
            needed = score(choice)[0]
            if needed > 0:
                bonus_letters = [c for c in set(choice) if self.bonus_alphabet.get(c, 0) > 0]
                logger.info(f"[LIVES] Vidas: '{choice}' (+{needed}) → Letras: {', '.join(sorted(bonus_letters))}")
        else:
            choice = random.choice(candidates)
        
        self.used_words.add(choice)
        return choice
