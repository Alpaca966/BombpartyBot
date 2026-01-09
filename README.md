# JKLM Bot - Automatización para BombParty

Bot inteligente para jugar automáticamente a BombParty (JKLM.fun) con múltiples estrategias y simulación de comportamiento humano.

## Características

- **Multi-idioma**: Soporte para español, inglés, alemán, francés, italiano y portugués(de Brasil).
- **Múltiples estrategias**: Random, palabras largas, palabras cortas, maximizar alfabeto bonus
- **Simulación humana**: Delays configurables para tecleo y pensamiento
- **Aprendizaje automático**: Aprende palabras nuevas y banea palabras inválidas
- **Interfaz visual**: Panel de control en el navegador con configuración en tiempo real
- **Sistema de logging**: Logs detallados con colores y niveles configurables
- **Persistencia**: Guarda automáticamente cambios en el diccionario
- **Altamente configurable**: Variables de entorno con `.env`

## Requisitos Previos

- **Python 3.8+**
- **pip**
- **Navegador web** (Testeado en Chrome)
- **Tampermonkey** (extensión de navegador)

## Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/Alpaca966/BombpartyBot
cd BombpartyBot
```

### 2. Crear entorno virtual (opcional pero recomendado)

**En Linux/Mac:**
```bash
python3 -m venv venv
source .venv/bin/activate
```

**En Windows:**
```bash
python -m venv venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar .env con tu configuración (opcional)
nano .env
```

### 5. Instalar script de Tampermonkey

1. Instala la extensión [Tampermonkey](https://www.tampermonkey.net/) en tu navegador
2. Abre `src/main.js`
3. Copia todo el contenido
4. En Tampermonkey: **Crear nuevo script** → pegar → **Guardar**

## Configuración

### Archivo `.env`

Puedes personalizar el comportamiento del bot editando `.env`:

```env
# Servidor WebSocket
HOST=localhost
PORT=8765

# Simulación humana (en segundos)
MIN_TYPING_DELAY=0.05      # Delay mínimo entre letras
MAX_TYPING_DELAY=0.15      # Delay máximo entre letras
START_DELAY_MIN=0.5        # Tiempo mínimo de "pensamiento"
START_DELAY_MAX=1.5        # Tiempo máximo de "pensamiento"

# Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

### Panel de Control del Navegador

Una vez iniciado, verás un panel en la esquina superior derecha de JKLM.fun con opciones:

- **Activar Bot**: Habilita/deshabilita el bot
- **Autounirse a Ronda**: Se une automáticamente cuando vuelves a la sala
- **Suicide**: Modo para perder vidas voluntariamente
- **Estrategias**: Selecciona cómo elegir palabras
- **Tiempos**: Ajusta delays en tiempo real
- **Enviar Frase**: Envía mensajes personalizados (Como si fuera una palabra de respuesta)

## Uso

### 1. Iniciar el servidor Python

```bash
python bot/main.py
```

### 2. Abrir JKLM.fun

1. Ve a [https://jklm.fun](https://jklm.fun)
2. Entra a una sala de BombParty
3. El script de Tampermonkey se activará automáticamente
4. Verás en consola: **"Conectado al servidor Python"**

### 3. Configurar y jugar

- Abre el panel del bot (esquina superior derecha)
- Activa el bot con el checkbox "Activar Bot"
- Selecciona tu estrategia preferida
- El bot jugará automáticamente



## Estructura del Proyecto

```
BombpartyBot/
├── bot/
│   ├── config.py           # Configuración centralizada
│   ├── main.py             # Punto de entrada del servidor
│   ├── logic/
│   │   └── solver.py       # Lógica de resolución de palabras
│   ├── network/
│   │   └── server.py       # Servidor WebSocket
│   └── utils/
│       ├── logger.py       # Sistema de logs
│       └── log_cleaner.py  # Utilidad para limpiar logs
├── data/
│   ├── diccionarios/       # Diccionarios de palabras por idioma
│   │   ├── es.txt
│   │   ├── en.txt
│   │   └── ...
│   └── logs/               # Archivos de log
│       ├── bot_server.log
│       └── packets.log
├── src/
│   └── main.js             # Script de Tampermonkey
├── .env                    # Configuración personal
├── .env.example            # Plantilla de configuración
├── .gitignore
├── requirements.txt        # Dependencias Python
└── README.md
```

## Licencia

Este proyecto es de código abierto para fines educativos.

## Disclaimer

Este bot es solo para fines educativos y de aprendizaje. El uso de bots está en contra de los términos de servicio de JKLM.fun. Úsalo bajo tu propia responsabilidad.


**Desarrollado por Alpaca** | Versión 2.0
