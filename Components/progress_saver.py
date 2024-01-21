import tkinter as tk
from tkinter import ttk

from placeholder_entry import PlaceholderEntry


class ProgessSaver(tk.Frame):
    def __init__(self, save_fn, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.save_fn = save_fn

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        page_entry_placeholder = ""
        timestamp_entry_placeholder = ""

        # Components
        self.label = tk.Label(self, text="Save Progress: ")
        self.label.grid(row=0, column=0, sticky="W", columnspan=3)

        self.page_label = tk.Label(self, text="Page to save: ")
        self.page_label.grid(row=1, column=0, sticky="W")

        self.page_entry = PlaceholderEntry(
            self, placeholder_text=page_entry_placeholder
        )
        self.page_entry.grid(row=1, column=1, sticky="WE", columnspan=2)

        self.timestamp_label = tk.Label(self, text="Timestamp to save: ")
        self.timestamp_label.grid(row=2, column=0, sticky="W")

        self.timestamp_entry = PlaceholderEntry(
            self, placeholder_text=timestamp_entry_placeholder
        )
        self.timestamp_entry.grid(row=2, column=1, sticky="WE", columnspan=2)

        self.progress_button = tk.Button(
            self, text="Save this progress", command=self.save_progress
        )
        self.progress_button.grid(row=3, column=0, sticky="W", pady=3)

    def save_progress(self):
        page_value = self.page_entry.get()
        time_value = self.timestamp_entry.get()

        self.save_fn(page_value, time_value)

        if self.page_entry:
            self.page_entry.clear_entry()
        if self.timestamp_entry:
            self.timestamp_entry.clear_entry()

    def reempty_entries(self):
        start_page_index = self.pdf_section.start_index
        stop_page_index = self.pdf_section.stop_index
        if self.page_entry:
            self.page_entry.clear_entry()
            self.page_entry.placeholder_text = f"{start_page_index+1}-{stop_page_index}"
            self.page_entry.on_focus_out("_")
        if self.timestamp_entry:
            self.timestamp_entry.clear_entry()
            self.timestamp_entry.placeholder_text = (
                f"00:00:00-{str(self.audio_handler.duration())}"
            )
            self.timestamp_entry.on_focus_out("_")
