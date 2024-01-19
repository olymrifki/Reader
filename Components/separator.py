import tkinter as tk
from tkinter import ttk


class Separator(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(height=5, relief=tk.SUNKEN, pady=10)
        self.separator = ttk.Separator(
            self,
            orient="horizontal",
        )
        self.separator.pack(fill="x")
