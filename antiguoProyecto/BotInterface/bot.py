from itertools import islice
from random import choice, randint, sample
from string import ascii_letters
from time import sleep

from socketio import Client


class Bot:
    roomSocket = Client(reconnection=False)
    gameSocket = Client(reconnection=False)

    def __init__(self, host, joinData, config):
        self.hostUrl = host
        self.joinData = joinData
        self.configGame = config
        self.connected = False
        self.bonusAlphabet = None
        self.bonusLetters = set()
        self.lastSyllable = ""
        self.lastWord = ""
        self.log = []
        self.disguiseChars = "jsaldkfjñ"
        self.usedWords = []
        self.writtenWords = []
        self.posibleWords = None
        self.ex = False
        self.maxLives = -1
        self.lives = 0
        self.forceLose = False
        self.valid_chars = "".join((ascii_letters, " ", "\n", "-", "'"))
        self.words = self._selectWordList(config['language'])

    def startBot(self):
        self._connectRoom()

    def _selectWordList(self, language) -> list:
        options = {
            'Spanish': r'txt\es.txt',
            'English': r'txt\en.txt',
            'Pokemon': r'txt\pokemons.txt'
        }
        return list(map(lambda x: x[:-1], (open(options[language], 'r', encoding='utf-8').readlines())))

    def _connectRoom(self):
        self.roomSocket.connect(self.hostUrl, transports=['websocket'])
        self.roomSocket.emit("joinRoom", self.joinData,
                             callback=self._onConnectedRoom)

    def _onConnectedRoom(self, data):
        self.selfPeerId = data['selfPeerId']
        self._connectGame()

    def _connectGame(self):
        self.gameSocket.connect(self.hostUrl, transports=['websocket'])
        self.gameSocket.emit("joinGame", data=(
            "bombparty", self.joinData['roomCode'], self.joinData['userToken']))
        self._joinRound()
        self.connected = True

    def _joinRound(self):
        sleep(0.5)
        self.gameSocket.emit("joinRound")

    def _filter_longs(self, words) -> filter:
        return islice(filter(lambda word: len(word) >= 20, words), 5)

    def _filter_lives(self, words) -> filter:
        lettersLeft = self.bonusAlphabet - self.bonusLetters

        def func(word):
            wordLetters = set(word)
            n = len(lettersLeft & wordLetters)
            return (n, word)

        lives = sorted((func(word) for word in words), reverse=True)

        return (word for _, word in lives)

    def _selectWord(self, syllable) -> filter:
        words = filter(
            lambda word: syllable in word and word not in self.usedWords, self.words)

        if self.configGame['lives']:
            words = self._filter_lives(words)

        if self.configGame['longs']:
            words = self._filter_longs(words)

        return words

    def _fakeWords(self):
        a = "".join(sample(self.disguiseChars, len(self.disguiseChars)))
        for x in range(len(a)):
            sleep(0.02)
            self.gameSocket.emit("setWord", data=(a[:x+1], False))
            if x == len(a)-1:
                self.gameSocket.emit("setWord", data=(a, True))

    def _disguise(self, word, wait):
        if not wait:
            if not randint(0, 1):
                self._fakeWords()
                sleep(0.5)
        # elif not randint(0, 4):
        #     sleep(0.5)
        #     self._fakeWords()
        #     sleep(0.5)
        else:
            sleep(choice([x/10 for x in range(5, 10)]))

        for i in range(len(word)):
            self.gameSocket.emit("setWord", data=(word[:i+1], False))

            if wait:
                sleep(choice([x/1000 for x in range(50, 115, 10)]))
            else:
                sleep(choice([x/1000 for x in range(30, 60, 10)]))

            if i == len(word)-1:
                self.gameSocket.emit("setWord", data=(word, True))

    def normalize(self, word) -> str:
        return "".join(filter(lambda char: char in self.valid_chars, word))

    def inputWord(self, syllable, wait=True):
        self.lastSyllable = syllable

        self.posibleWords = self._selectWord(
            syllable) if self.posibleWords is None else self.posibleWords

        word = next(self.posibleWords, None)

        if not word:
            word = next(filter(
                lambda word: syllable in word and word not in self.usedWords, self.words), "NONE")
        
        # self.console_window.write(f"Word: {word}")

        if self.configGame['disguise']:
            self._disguise(word, wait)
        else:
            self.gameSocket.emit("setWord", data=(word, True))

        self.usedWords.append(word)

    def lose(self, syllable):
        if self.lives != self.maxLives:
            self.gameSocket.emit("setWord", data=("💥", True))
        else:
            self.inputWord(syllable)

