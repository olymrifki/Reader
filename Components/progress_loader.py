import tkinter as tk
from tkinter import ttk

from list_selector import ListSelector


class ProgessLoader(tk.Frame):
    def __init__(self, bookmark, past_progress, open_audio, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # self.configure(background="red")

        self.progress_label = tk.Label(self, text="Select Where to Start: ")
        self.progress_label.grid(row=0, column=0, sticky="W", columnspan=3)

        self.bookmark_label = tk.Label(self, text="Select from bookmark")
        self.bookmark_label.grid(row=1, column=0, sticky="W")
        self.bookmark_menu = ListSelector(
            bookmark[0],
            bookmark[1],
            bookmark[2],
            self,
        )
        self.bookmark_menu.grid(row=1, column=1, sticky="WE", columnspan=2)

        self.previous_progress_label = tk.Label(self, text="Or get past progress")
        self.previous_progress_label.grid(row=2, column=0, sticky="W")
        self.saved_progress_menu = ListSelector(
            past_progress[0],
            past_progress[1],
            past_progress[2],
            self,
        )
        self.saved_progress_menu.grid(row=2, column=1, sticky="WE", columnspan=2)
        self.process_audio_button = tk.Button(
            self, text="Read and listen from here", command=open_audio
        )
        self.process_audio_button.grid(row=3, column=0, sticky="W", pady=3)
