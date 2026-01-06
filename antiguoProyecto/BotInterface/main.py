import customtkinter as ctk
from requests import post

from interface import Interface, Console
from bot import Bot


class App(Interface, Bot):
    def __init__(self):
        Interface.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.QUIT)

        self.console = None
        self.bot = None

        self.commandsHelp = {
            'lives': 'activates/deactivates lives. lievs/lv',
            'longs': 'activates/deactivates longs. longs/lo',
            'disguise': 'activates/deactivates disguise. disguise/dg',
            'lose': 'loses lives until the command is retyped. lose/ls',
            'config': 'show config',
            'help': 'commands: lives/lv, longs/lo, disguise/dg, lose/ls, config',
        }

        self.commandsSynonyms = {
            'lv': 'lives',
            'lo': 'longs',
            'dg': 'disguise',
            'ls': 'lose'
        }

        self.preJoinData = {
            "roomCode": "",
            "nickname": "",
            "userToken": "abcdefghijklmnop",
            "language": "es-ES",
            "gameId": "bombparty",
            "auth": None,
            "picture": None
        }

        self.preConfig = {
            "disguise": None,
            "lives": None,
            "longs": None,
            "language": None
        }

    def _changeConfig(self, var):
        self.configGame[var] = not self.configGame[var]
        self.console.writeCommandResponse(
            var + ": " + str(self.configGame[var]))

    def _showConfig(self):
        self.console.writeCommandResponse(
            f"lives: {self.configGame['lives']}\nlongs: {self.configGame['longs']}\ndisguise: {self.configGame['disguise']}")

    def _start(self):
        if self.console is None or not self.console.winfo_exists():
            self.console = Console(self)

        elif self.console.winfo_exists():
            self.console.focus()

        if not self.roomSocket.connected:
            data = self.get_data()
            host = self.checkData(data)

            if host is not None:
                if host.get("url", None):
                    self.run(host['url'])
                    self.console.writeCommandResponse(
                        "https://jklm.fun/"+self.preJoinData['roomCode'])
                else:
                    self.console.writeAlert(host['errorCode'])

    def _emitMessage(self, *data):
        message = self.chatEntry.get()
        self.chatEntry.delete("0", ctk.END)
        self.roomSocket.emit("chat", message)

    def _writeChatMessage(self, nickname, message):
        self.chatBox.insert(ctk.END, f"{nickname}: {message}\n")
        self.chatBox.see(ctk.END)

    def checkData(self, data) -> dict:
        if len(data['roomCode']) != 4:
            self.console.writeAlert("Invalid room code")
            return

        if len(data['nickname']) > 20 or len(data['nickname']) < 3:
            self.console.writeAlert("Invalid nickname")
            return

        host = self.getHost(data['roomCode'])
        self.saveData(data)

        return host

    def saveData(self, data):
        self.preJoinData['roomCode'] = data['roomCode']
        self.preJoinData['nickname'] = data['nickname']

        self.preConfig['lives'] = data['lives']
        self.preConfig['longs'] = data['longs']
        self.preConfig['disguise'] = data['disguise']
        self.preConfig['language'] = data['language']

    def getHost(self, roomCode):
        return post(
            "https://jklm.fun/api/joinRoom", json={"roomCode": roomCode}).json()

    def consoleData(self, *data):
        command = self.console.consoleEntry.get().lower()
        self.console.consoleEntry.delete("0", ctk.END)

        self.console.writeCommand(command)
        self.console.consoleBox.see('end')

        self.proccesConsoleData(command)

    def proccesConsoleData(self, command: str):
        command = command.split()

        if not len(command) or command[0] not in self.commandsHelp.keys() and command[0] not in self.commandsSynonyms.keys():
            self.console.writeCommandResponse("unknown command")
        else:
            if command[0] == "help" and command[-1] in self.commandsHelp.keys():
                self.console.writeCommandResponse(
                    self.commandsHelp[command[-1]])
            elif command[0] == "config" and self.roomSocket.connected:
                self._showConfig()
            elif (command[0] == "lose" or command[0] == "ls") and self.roomSocket.connected:
                self.forceLose = not self.forceLose
                self.console.writeCommandResponse("lose: "+str(self.forceLose))
            elif (command[0] in self.commandsHelp.keys() or command[0] in self.commandsSynonyms.keys()) and not self.roomSocket.connected:
                self.console.writeCommandResponse(
                    "unavailable command, not connected")
            else:
                if command[0] in self.commandsHelp.keys():
                    self._changeConfig(command[0])
                elif command[0] in self.commandsSynonyms:
                    self._changeConfig(self.commandsSynonyms[command[0]])

    def run(self, host):
        Bot.__init__(self, host, self.preJoinData, self.preConfig)
        self.startBot()

# --------------------RoomEvents--------------------------------------------


@App.roomSocket.event
def connect():
    app.console.writeAlert("Connected to the ROOM")


@App.roomSocket.event
def disconnect():
    app.console.writeAlert("Disconnected from the ROOM")


@App.roomSocket.event
def chat(info, message):
    app._writeChatMessage(info['nickname'], message)

# --------------------GameEvents--------------------------------------------


@App.gameSocket.event
def connect():
    app.console.writeAlert("Connected to the GAME")


@App.gameSocket.event
def disconnect():
    app.console.writeAlert("Disconnected from the GAME")


@App.gameSocket.event
def nextTurn(playerPeerId, syllable, promptAge):
    if playerPeerId == app.selfPeerId:
        if app.forceLose:
            app.lose(syllable)
        else:
            app.inputWord(syllable)
    else:
        app.posibleWords = None


@App.gameSocket.event
def setMilestone(*data):
    app.forceLose = False
    if data[0]['name'] == "round" and data[0]['currentPlayerPeerId'] == app.selfPeerId:
        app.inputWord(data[0]['syllable'])
    elif data[0]['name'] == "seating":
        app._joinRound()
        app.usedWords.clear()


@App.gameSocket.event
def setPlayerWord(playerPeerId, word):
    app.lastWord = word


@App.gameSocket.event
def failWord(playerPeerId, reason):
    if playerPeerId == app.selfPeerId and reason == "notInDictionary":
        app.words.remove(app.usedWords[-1])
        app.inputWord(app.lastSyllable, wait=False)
    elif playerPeerId == app.selfPeerId and reason == "alreadyUsed":
        app.inputWord(app.lastSyllable, wait=False)


@App.gameSocket.event
def correctWord(data):
    if data['playerPeerId'] != app.selfPeerId:
        app.usedWords.append(app.normalize(app.lastWord))
    else:
        app.bonusLetters = set(data['bonusLetters'])


@App.gameSocket.event
def bonusAlphabetCompleted(playerPeerId, lives):
    if playerPeerId == app.selfPeerId:
        app.lives = lives


@App.gameSocket.event
def livesLost(playerPeerId, lives):
    if playerPeerId == app.selfPeerId:
        app.lives = lives


@App.gameSocket.event
def setup(data):
    app.bonusAlphabet = set(
        data['milestone']['dictionaryManifest']['bonusAlphabet'])


app = App()
app.mainloop()
