import tkinter as tk

from list_selector import ListSelector


class ProgessDeleter(tk.Frame):
    def __init__(self, delete_fn, past_progress, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Components
        self.label = tk.Label(self, text="Finish Reading? Delete the Progress: ")
        self.label.grid(row=0, column=0, sticky="W", columnspan=3)

        self.delete_bookmark_label = tk.Label(self, text="Progress to delete: ")
        self.delete_bookmark_label.grid(row=1, column=0, sticky="W")

        self.delete_progress_menu = ListSelector(
            past_progress[0],
            past_progress[1],
            past_progress[2],
            self,
        )
        self.delete_progress_menu.grid(row=1, column=1, sticky="WE", columnspan=2)

        self.delete_a_bookmark_button = tk.Button(
            self, text="Delete bookmark", command=delete_fn
        )
        self.delete_a_bookmark_button.grid(row=2, column=0, sticky="W")
