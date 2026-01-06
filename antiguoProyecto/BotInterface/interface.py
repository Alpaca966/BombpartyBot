import customtkinter as ctk
import sys


ctk.set_default_color_theme("dark-blue")


class Interface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x500")
        self.minsize(width=700, height=289)
        self.title("JKLM.fun Bot")
        self.quit_window = None

        self.create_infoSidebar()
        self.create_configSidebar()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        self.chat_Frame = ctk.CTkFrame(self, fg_color="#1A1A1A")
        self.chat_Frame.grid_rowconfigure(1, weight=1)
        self.chat_Frame.grid_columnconfigure(0, weight=1)

        self.chatbox_label = ctk.CTkLabel(
            self.chat_Frame, text="Room Chat", font=ctk.CTkFont(weight=("bold")))
        self.chatBox = ctk.CTkTextbox(self.chat_Frame)
        self.chatEntry = ctk.CTkEntry(self.chat_Frame)

        self.chat_Frame.grid(row=0, column=2, rowspan=2,
                             columnspan=2, pady=10, padx=10, sticky="nswe")
        self.chatbox_label.grid()
        self.chatBox.grid(sticky="nswe")
        self.chatEntry.grid(pady=(5, 0), sticky="nswe")
        self.chatEntry.bind("<Return>", self._emitMessage)

    def create_infoSidebar(self):
        self.info_sidebar_frame = ctk.CTkFrame(
            self, fg_color="#1A1A1A")

        self.info_label = ctk.CTkLabel(
            self.info_sidebar_frame, text="Info", font=ctk.CTkFont(size=30, weight=("bold")), anchor="w"
        )

        self.nickname_entry_label = ctk.CTkLabel(
            self.info_sidebar_frame, text="Nickname", font=ctk.CTkFont(weight=("bold"))
        )

        self.nickname_entry = ctk.CTkEntry(
            self.info_sidebar_frame, placeholder_text="Nickname"
        )

        self.roomCode_entry_label = ctk.CTkLabel(
            self.info_sidebar_frame, text="Room code", font=ctk.CTkFont(weight=("bold"))
        )

        self.roomCode_entry = ctk.CTkEntry(
            self.info_sidebar_frame, placeholder_text="RoomCode", text_color="#00FF00"
        )

        self.info_sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.info_label.grid(row=0, padx=20, pady=(20, 10))
        self.nickname_entry_label.grid(row=1, padx=12, sticky="w")
        self.nickname_entry.grid(row=2, padx=10, pady=(0, 10))
        self.roomCode_entry_label.grid(row=3, padx=12, sticky="w")
        self.roomCode_entry.grid(row=4, padx=10, pady=(0, 10))

        self.info_bottom_frame = ctk.CTkFrame(self, fg_color="#1A1A1A")

        self.start_buttom = ctk.CTkButton(
            self.info_bottom_frame, text="Start", command=self._start, font=ctk.CTkFont(weight=("bold"))
        )

        self.quit_buttom = ctk.CTkButton(
            self.info_bottom_frame, text="QUIT", command=self.QUIT, font=ctk.CTkFont(weight=("bold"))
        )

        self.info_bottom_frame.grid(row=1, column=0)
        self.start_buttom.grid(pady=(0, 10))
        self.quit_buttom.grid(pady=(0, 10))

    def create_configSidebar(self):
        self.livesVar = ctk.BooleanVar()
        self.longsVar = ctk.BooleanVar()
        self.disguiseVar = ctk.BooleanVar()
        self.languageVar = ctk.StringVar(value="Spanish")

        self.config_sidebar_frame = ctk.CTkFrame(
            self, fg_color="#1A1A1A"
        )

        self.config_label = ctk.CTkLabel(
            self.config_sidebar_frame, text="Config", font=ctk.CTkFont(size=30, weight=("bold")), anchor="w"
        )

        self.lifes_checkbox = ctk.CTkCheckBox(
            self.config_sidebar_frame, variable=self.livesVar, text="Lifes", font=ctk.CTkFont(weight=("bold"))
        )

        self.longs_checkbox = ctk.CTkCheckBox(
            self.config_sidebar_frame, variable=self.longsVar, text="Longs", font=ctk.CTkFont(weight=("bold"))
        )

        self.disguise_checkbox = ctk.CTkCheckBox(
            self.config_sidebar_frame, variable=self.disguiseVar, text="Disguise", font=ctk.CTkFont(weight=("bold"))
        )

        self.language_optionMenu = ctk.CTkOptionMenu(
            self.config_sidebar_frame, values=["Spanish", "English", "Pokemon"], variable=self.languageVar, font=ctk.CTkFont(weight=("bold"))
        )

        self.config_sidebar_frame.grid(
            row=0, column=1, rowspan=4, sticky="nsew")
        self.config_label.grid(row=0, padx=20, pady=(20, 10))
        self.lifes_checkbox.grid(row=1, padx=10, pady=10)
        self.longs_checkbox.grid(row=2, padx=10, pady=10)
        self.disguise_checkbox.grid(row=3, padx=10, pady=10)
        self.language_optionMenu.grid(row=4, padx=10, pady=10)

    def QUIT(self):
        if self.roomSocket.connected:
            self.roomSocket.disconnect()
            self.gameSocket.disconnect()
        sys.exit()

    def get_data(self) -> dict[str]:
        data = {
            'roomCode': self.roomCode_entry.get().upper(),
            'nickname': self.nickname_entry.get(),
            'lives': self.livesVar.get(),
            'longs': self.longsVar.get(),
            'disguise': self.disguiseVar.get(),
            'language': self.languageVar.get(),
        }
        return data


class Console(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__()

        self.title("Console")
        self.geometry("300x150")
        self.attributes("-topmost", True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.consoleBox = ctk.CTkTextbox(self)
        self.consoleBox.configure()
        self.consoleEntry = ctk.CTkEntry(self)
        self.consoleEntry.bind("<Return>", app.consoleData)

        self.consoleBox.grid(sticky="nswe")
        self.consoleEntry.grid(pady=(5, 0), sticky="nswe")

    def writeAlert(self, message):
        self.consoleBox.insert(ctk.END, "!! " + message + "\n")
        self.consoleBox.see(ctk.END)

    def writeCommand(self, message):
        self.consoleBox.insert(ctk.END, "> " + message + "\n")
        self.consoleBox.see(ctk.END)

    def writeCommandResponse(self, message):
        self.consoleBox.insert(ctk.END, message + "\n")
        self.consoleBox.see(ctk.END)
