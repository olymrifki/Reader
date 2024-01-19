import tkinter as tk
from tkinter import ttk


class LabelledSearchInput(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # self.configure(background="red")

        self.label = tk.Label(self, text="Select PDF: ")
        self.label.grid(row=0, column=0, sticky="W", columnspan=2)

        self.path_entry = tk.Entry(self)
        self.path_entry.grid(padx=5, row=1, column=0, sticky="WE")
        self.get_path_button = tk.Button(
            self, text="Get PDF", command=self.input_and_start_PDFreader
        )
        self.get_path_button.grid(row=1, column=1, sticky="W")

    def input_and_start_PDFreader():
        return
