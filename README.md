# JKLM Bot - BombParty Automation

Intelligent bot to automatically play BombParty (JKLM.fun) with multiple strategies and human behavior simulation.

## Features

- **Multi-language**: Support for Spanish, English, German, French, Italian, and Portuguese (Brazilian).
- **Multiple strategies**: Random, long words, short words, maximize bonus alphabet
- **Human simulation**: Configurable delays for typing and thinking
- **Auto-learning**: Learns new words and bans invalid words
- **Visual interface**: In-browser control panel with real-time configuration
- **Logging system**: Detailed logs with colors and configurable levels
- **Persistence**: Automatically saves dictionary changes
- **Highly configurable**: Environment variables with `.env`

## Prerequisites

- **Python 3.8+**
- **pip**
- **Web browser** (Tested on Chrome)
- **Tampermonkey** (browser extension)

## Installation

### 1. Clone or download the project

```bash
git clone https://github.com/Alpaca966/BombpartyBot
cd BombpartyBot
```

### 2. Create virtual environment (optional but recommended)

**On Linux/Mac:**
```bash
python3 -m venv venv
source .venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy configuration template
cp .env.example .env

# Edit .env with your configuration (optional)
nano .env
```

### 5. Install Tampermonkey script

1. Install the [Tampermonkey](https://www.tampermonkey.net/) extension in your browser
2. **Important:** Enable Developer Mode to allow script execution: [Q209: Permission to execute userscripts](https://www.tampermonkey.net/faq.php?locale=en#Q209)
3. Open `tamperMonkey/main.js`
4. Copy all the content
5. In Tampermonkey: **Create new script** → paste → **Save**

## Configuration

### `.env` File

You can customize the bot's behavior by editing `.env`:

```env
# WebSocket Server
HOST=localhost
PORT=8765

# Human simulation (in seconds)
MIN_TYPING_DELAY=0.05      # Minimum delay between letters
MAX_TYPING_DELAY=0.15      # Maximum delay between letters
START_DELAY_MIN=0.5        # Minimum "thinking" time
START_DELAY_MAX=1.5        # Maximum "thinking" time

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

### Browser Control Panel

Once started, you'll see a panel in the top-right corner of JKLM.fun with options:

- **Activate Bot**: Enable/disable the bot
- **Auto-join Round**: Automatically joins when you return to the room
- **Suicide**: Mode to lose lives voluntarily
- **Strategies**: Select how to choose words
- **Timings**: Adjust delays in real-time
- **Send Phrase**: Send custom messages (As if it were a response word)

## Usage

### 1. Start the Python server

```bash
python bot/main.py
```

### 2. Open JKLM.fun

1. Go to [https://jklm.fun](https://jklm.fun)
2. Enter a BombParty room
3. The Tampermonkey script will activate automatically
4. You'll see in console: **"Connected to Python server"**

### 3. Configure and play

- Open the bot panel (top-right corner)
- Activate the bot with the "Activate Bot" checkbox
- Select your preferred strategy
- The bot will play automatically



## Project Structure

```
BombpartyBot/
├── bot/
│   ├── config.py           # Centralized configuration
│   ├── main.py             # Server entry point
│   ├── logic/
│   │   └── solver.py       # Word solving logic
│   ├── network/
│   │   └── server.py       # WebSocket server
│   └── utils/
│       ├── logger.py       # Logging system
│       └── log_cleaner.py  # Utility to clean logs
├── data/
│   ├── diccionarios/       # Word dictionaries by language
│   │   ├── es.txt
│   │   ├── en.txt
│   │   └── ...
│   └── logs/               # Log files
│       ├── bot_server.log
│       └── packets.log
├── src/
│   └── main.js             # Tampermonkey script
├── .env                    # Personal configuration
├── .env.example            # Configuration template
├── .gitignore
├── requirements.txt        # Python dependencies
└── README.md
```

## License

This project is open source for educational purposes.

## Disclaimer

This bot is for educational and learning purposes only. The use of bots is against JKLM.fun's terms of service. Use it at your own risk.


**Developed by Alpaca** | Version 2.0
