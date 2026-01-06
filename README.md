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
- **pip** (gestor de paquetes de Python)
- **Navegador web** (Chrome, Firefox, Edge)
- **Tampermonkey** (extensión de navegador)

## Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/Alpaca966/BombpartyBot
cd jklmfunBotTampermonkey
```

### 2. Crear entorno virtual (opcional pero recomendado)

**En Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**En Windows:**
```bash
python -m venv .venv
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

Deberías ver:
```
[INIT] JKLM Bot - Iniciando sistema...
[INIT] Iniciando servidor en ws://localhost:8765
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

## Estrategias Disponibles

| Estrategia | Descripción |
|------------|-------------|
| **Random** | Elige palabras aleatorias |
| **Maximizar Longitud** | Prioriza palabras largas |
| **Modo Pánico (Cortas)** | Usa palabras cortas |
| **Maximizar Alfabeto** | Completa letras bonus |

## Estructura del Proyecto

```
jklmfunBotTampermonkey/
├── bot/
│   ├── config.py           # Configuración centralizada
│   ├── main.py             # Punto de entrada del servidor
│   ├── logic/
│   │   └── solver.py       # Lógica de resolución de palabras
│   ├── network/
│   │   └── server.py       # Servidor WebSocket
│   └── utils/
│       ├── logger.py       # Sistema de logging
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
├── .env                    # Configuración personal (no subir a Git)
├── .env.example            # Plantilla de configuración
├── .gitignore
├── requirements.txt        # Dependencias Python
└── README.md
```

## Solución de Problemas

### El bot no se conecta

**Problema:** No aparece "Conectado al servidor Python"

**Solución:**
1. Verifica que el servidor Python se esté ejecutando
2. Comprueba que el puerto 8765 no esté ocupado
3. Revisa la consola del navegador (F12) para ver errores

### El bot no responde / no escribe

**Problema:** El bot no juega su turno

**Soluciones:**
- Verifica que "Activar Bot" esté marcado
- Comprueba los logs: `data/logs/bot_server.log` y `data/logs/packets.log`
- Asegúrate de que el evento `setup` se recibió (aparece en logs)
- Si no llega setup, recarga la página

### Puerto ocupado

**Problema:** Error "Address already in use"

**Solución:**
```bash
# Cambiar puerto en .env
PORT=9000
```

Y actualizar en `src/main.js`:
```javascript
const PYTHON_URL = "ws://localhost:9000";
```

### Palabras incorrectas

**Problema:** El bot usa palabras que no existen

**Solución:**
- Las palabras se banean automáticamente tras fallar
- Revisa el diccionario en `data/diccionarios/`
- El bot aprende palabras nuevas automáticamente

### Logs demasiado verbosos

**Problema:** Muchos logs en consola

**Solución:**
Cambia el nivel en `.env`:
```env
LOG_LEVEL=WARNING  # Solo advertencias y errores
```

## Desarrollo

### Ejecutar en modo debug

```env
# .env
LOG_LEVEL=DEBUG
```

Verás todos los packets enviados/recibidos.

## Logs

El bot genera dos archivos de log:

- **`bot_server.log`**: Eventos principales del bot
- **`packets.log`**: Tráfico de red completo (solo con LOG_LEVEL=DEBUG)

## Licencia

Este proyecto es de código abierto para fines educativos.

## Disclaimer

Este bot es solo para fines educativos y de aprendizaje. El uso de bots puede estar en contra de los términos de servicio de JKLM.fun. Úsalo bajo tu propia responsabilidad.

## Soporte

Si encuentras problemas:
1. Revisa la sección de Solución de Problemas
2. Consulta los logs para más información
3. Los modelos LLM están para algo... :D

---

**Desarrollado por Alpaca** | Versión 2.0
