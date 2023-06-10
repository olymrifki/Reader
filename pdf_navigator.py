import os
import sqlite3
import time
import tkinter as tk
import wave
from datetime import datetime, timedelta
from tkinter import filedialog, ttk

import pygetwindow as gw

from audio_opener import AudioOpener
from const import *
from pdf2text import Pdf2Text
from pdf_handler import PDFHandler, PDFSection
from placeholder_entry import PlaceholderEntry
from text2speech import Text2Speech


class PDFNavigator(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = sqlite3.connect("reading_data.db")
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.is_bookmark_chosen = False

        self.is_initial_loaded = False
        self.is_loader_loaded = False
        self.is_saving_loaded = False
        self.row_number = 0
        self.chosen_pdf = tk.StringVar()
        self.generated_audio_file = tk.StringVar()
        self.audio_directory = "D:/requested_audios/"

        self._setup_initial_gui_components()

    def _increment_row_number(self):
        self.row_number += 1

    def _setup_initial_gui_components(self):
        """Define and place tkinter components for initial application interface."""

        if not self.is_initial_loaded:
            # Components
            self.title_0_label = tk.Label(self, text="Select PDF: ")
            self.path_entry = tk.Entry(self)
            self.get_path_button = tk.Button(
                self, text="Get PDF", command=self.input_and_start_PDFreader
            )
            self.separator_frame0 = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
            self.separator0 = ttk.Separator(self.separator_frame0, orient="horizontal")

            # Placements
            self.title_0_label.grid(
                row=self.row_number, column=0, sticky="W", columnspan=2
            )
            self._increment_row_number()
            self.path_entry.grid(padx=5, row=self.row_number, column=0, sticky="WE")
            self.get_path_button.grid(row=self.row_number, column=1, sticky="W")
            self._increment_row_number()
            self.separator_frame0.grid(
                row=self.row_number, column=0, columnspan=2, sticky="EW", pady=10
            )
            self.separator0.pack(fill="x", expand=True)
            self._increment_row_number()

            self._reconfigure_column_space()
        self.is_initial_loaded = True

    def _setup_loader_components(self):
        """Define and place tkinter components for book section loader application interface."""

        if not self.is_loader_loaded:
            tk_window = gw.getWindowsWithTitle("App Window")[0]
            tk_window.moveTo(int(SCREEN_WIDTH * 0.7), 0)

            self.bookmark_pages_list = [
                str(section) for section in self.pdf_handler.get_sorted_section_list()
            ]
            self.past_progress = self.get_saved_data()
            self.bookmark_choice = tk.StringVar()
            self.bookmark_choice.trace("w", self._bookmark_choice_changed)
            self.past_progress_bookmark_choice = tk.StringVar()
            self.past_progress_bookmark_choice.trace(
                "w", self._past_progress_choice_changed
            )

            # Components
            self.title_1_label = tk.Label(self, text="Select Where to Start: ")
            self.bookmark_label = tk.Label(self, text="Select from bookmark")
            self.menu = tk.OptionMenu(
                self, self.bookmark_choice, *self.bookmark_pages_list
            )
            self.previous_progress_label = tk.Label(self, text="Or get past progress")
            self.progress_menu = tk.OptionMenu(
                self, self.past_progress_bookmark_choice, *self.past_progress
            )
            self.process_audio_button = tk.Button(
                self, text="Read and listen from here", command=self.open_audio
            )
            self.separator_frame2 = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
            self.separator2 = ttk.Separator(self.separator_frame2, orient="horizontal")

            # Placements
            self.title_1_label.grid(
                row=self.row_number, column=0, sticky="W", columnspan=2
            )
            self._increment_row_number()
            self.bookmark_label.grid(column=0, row=self.row_number, sticky="W")
            self.menu.grid(column=1, row=self.row_number, sticky="W")
            self._increment_row_number()
            self.previous_progress_label.grid(
                pady=5, column=0, row=self.row_number, sticky="W"
            )
            self.progress_menu.grid(column=1, row=self.row_number, sticky="W")
            self._increment_row_number()
            self.process_audio_button.grid(
                padx=5, column=0, row=self.row_number, columnspan=2, sticky="W"
            )
            self._increment_row_number()
            self.separator_frame2.grid(
                row=self.row_number, column=0, columnspan=2, sticky="EW", pady=10
            )
            self.separator2.pack(fill="x", expand=True)
            self._increment_row_number()

            self._reconfigure_column_space()
        self.is_loader_loaded = True

    def _setup_saving_components(self):
        """Define and place tkinter components for saving progress loader application interface."""

        if not self.is_saving_loaded:
            page_entry_placeholder = ""
            timestamp_entry_placeholder = ""

            # Components
            self.title_3_label = tk.Label(self, text="Save Progress: ")
            self.save_page_label = tk.Label(self, text="Page to save: ")
            self.page_entry = PlaceholderEntry(
                self, placeholder_text=page_entry_placeholder
            )
            self.save_timestamp_label = tk.Label(self, text="Timestamp to save: ")
            self.timestamp_entry = PlaceholderEntry(
                self, placeholder_text=timestamp_entry_placeholder
            )
            self.save_progress_button = tk.Button(
                self, text="Save this progress", command=self.save_progress
            )
            self.separator_frame3 = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
            self.separator3 = ttk.Separator(self.separator_frame3, orient="horizontal")

            # Placements
            self.title_3_label.grid(
                row=self.row_number, column=0, sticky="W", columnspan=2
            )
            self._increment_row_number()
            self.save_page_label.grid(column=0, row=self.row_number, sticky="W")
            self.page_entry.grid(column=1, row=self.row_number, sticky="W")
            self._increment_row_number()
            self.save_timestamp_label.grid(column=0, row=self.row_number, sticky="W")
            self.timestamp_entry.grid(column=1, row=self.row_number, sticky="W")
            self._increment_row_number()
            self.save_progress_button.grid(
                padx=5, column=0, row=self.row_number, columnspan=2, sticky="W"
            )
            self._increment_row_number()
            self.separator_frame3.grid(
                row=self.row_number, column=0, columnspan=2, sticky="EW", pady=10
            )
            self.separator3.pack(fill="x", expand=True)
            self._increment_row_number()

            self._reconfigure_column_space()

        self.is_saving_loaded = True

    def _reconfigure_column_space(self):
        for col in range(self.grid_size()[0]):
            self.grid_columnconfigure(col, weight=1)

    def input_and_start_PDFreader(self):
        """Callback for Get PDF button"""
        pdf_filename = self._input_pdf_filename()
        if pdf_filename.endswith(".pdf"):
            self.chosen_pdf.set(pdf_filename)
            self.pdf_handler = PDFHandler(pdf_filename)
            self._setup_loader_components()

    def _input_pdf_filename(self):
        """Use tkinter filedialog to browse folder structures and"""
        filetypes = (("PDF Files", "*.pdf"),)
        pdf_filename = filedialog.askopenfilename(filetypes=filetypes)
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(tk.END, pdf_filename)
        return pdf_filename

    def _bookmark_choice_changed(self, *args):
        self.is_bookmark_chosen = True

        self.pdf_section = self.pdf_handler.get_section_from_bookmark(
            bookmark=self.bookmark_choice.get()
        )

    def _past_progress_choice_changed(self, *args):
        self.is_bookmark_chosen = False

        self.pdf_section = self.pdf_handler.get_section_from_bookmark(
            bookmark=self.past_progress_bookmark_choice.get()
        )

    def _open_pdf_app(self):
        self.pdf_handler.open_pdf_with_sumatrapdf_at(section=self.pdf_section)

        while not gw.getWindowsWithTitle("SumatraPDF"):
            time.sleep(0.1)
        time.sleep(0.5)
        pdf_reader_window = gw.getWindowsWithTitle("SumatraPDF")[0]
        pdf_reader_window.moveTo(0, 0)
        pdf_reader_window.resizeTo(int(SCREEN_WIDTH * 0.7), SCREEN_HEIGHT)

    # refactored up to here

    def open_audio(self):
        if self.is_bookmark_chosen == True:
            print("\n\nLoad new audio\n\n")
            start_page_index = self.pdf_section.start_index
            stop_page_index = self.pdf_section.stop_index
            self._open_pdf_app()

            # get_tts_text
            p2t = Pdf2Text(self.chosen_pdf.get())
            text = p2t.extract_text(start_page_index, stop_page_index)

            # convert text to speech
            tts = Text2Speech()
            self._generate_audio_file_name(start_page_index, stop_page_index)
            tts.convert(text, filename=self.generated_audio_file.get())

            self._open_audio_app()

        elif self.is_bookmark_chosen == False:
            print("\n\nLoad past audio\n\n")
            past_data = self.load_past_data(self.past_progress_bookmark_choice.get())[0]
            # "bookmark"
            self.bookmark_choice.set(past_data["bookmark"])
            self.is_bookmark_chosen = False

            self.pdf_section.start_index = int(past_data["last_page_index"])
            start_page_index = int(past_data["last_page_index"])
            stop_page_index = self.pdf_section.stop_index
            self.generated_audio_file.set(past_data["audio_path"])
            self._open_pdf_app()
            self._open_audio_app(start_at=past_data["last_time"])

        self._setup_saving_components()
        if self.page_entry:
            self.page_entry.clear_entry()
            self.page_entry.placeholder_text = f"{start_page_index+1}-{stop_page_index}"
            self.page_entry.on_focus_out("_")
        if self.timestamp_entry:
            self.timestamp_entry.clear_entry()
            self.timestamp_entry.placeholder_text = (
                f"00:00:00-{self.timedelta_to_string(self.get_audio_duration())}"
            )
            self.timestamp_entry.on_focus_out("_")

    def _generate_audio_file_name(self, start_page_index, stop_page_index):
        filename_without_extension = os.path.splitext(
            os.path.basename(self.chosen_pdf.get())
        )[0]
        self.generated_audio_file.set(
            self.audio_directory
            + filename_without_extension
            + "_"
            + str(start_page_index + 1)
            + "-"
            + str(stop_page_index + 1)
            + ".wav"
        )

    def _open_audio_app(self, start_at=None):
        for sound_player_window in gw.getWindowsWithTitle("PotPlayer"):
            sound_player_window.close()
        ao = AudioOpener(self.generated_audio_file.get())

        if start_at is None:
            ao.open_file_with_potplayer()
        else:
            ao.open_file_with_potplayer(start_at)
        while not gw.getWindowsWithTitle("PotPlayer"):
            time.sleep(0.1)
        time.sleep(3)
        sound_player_window = gw.getWindowsWithTitle("PotPlayer")[0]
        sound_player_window.moveTo(int(SCREEN_WIDTH * 0.7), int(SCREEN_HEIGHT * 0.7))
        sound_player_window.resizeTo(int(SCREEN_WIDTH * 0.3), int(SCREEN_HEIGHT * 0.3))

    def get_audio_duration(self):
        with wave.open(self.generated_audio_file.get()) as mywav:
            duration_seconds = mywav.getnframes() / mywav.getframerate()

        return timedelta(seconds=duration_seconds)

    def validate_time_input(self, time_input):
        time_input = self.string_to_timedelta(time_input)
        if not (
            time_input > timedelta(seconds=0) and time_input < self.get_audio_duration()
        ):
            return
        return self.timedelta_to_string(time_input)

    def validate_page_input(self, stop_page_input):
        stop_page_index_input = int(stop_page_input) - 1

        if not (
            stop_page_index_input >= self.pdf_section.start_index
            and stop_page_index_input < self.pdf_section.stop_index
        ):
            return
        return stop_page_index_input

    def timedelta_to_string(self, delta):
        total_seconds = delta.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def string_to_timedelta(self, time_str):
        time_parts = time_str.split(":")
        if len(time_parts) == 3:
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = int(time_parts[2])
        elif len(time_parts) == 2:
            hours = 0
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])

        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def update_choices(self):
        new_choices = self.get_saved_data()
        self.past_progress = new_choices
        # Update the OptionMenu
        menu = self.progress_menu["menu"]
        menu.delete(0, "end")
        for choice in self.past_progress:
            menu.add_command(
                label=choice,
                command=lambda value=choice: self.past_progress_bookmark_choice.set(
                    value
                ),
            )

    def save_progress(self):
        print("getting data")
        stop_page_index = self.validate_page_input(self.page_entry.get())
        stop_time = self.validate_time_input(self.timestamp_entry.get())
        if not stop_page_index or not stop_time:
            return
        bookmark = self.bookmark_choice.get()

        print("data retrieved, saving...")
        if self.is_bookmark_chosen == False:
            self.cursor.execute(
                "UPDATE past_reading_progress SET bookmark = ?, last_page_index = ?, last_time=? WHERE audio_path = ? AND pdf_path = ?",
                (
                    bookmark,
                    stop_page_index,
                    stop_time,
                    self.generated_audio_file.get(),
                    self.chosen_pdf.get(),
                ),
            )
            self.db.commit()
            label = "Data updated"
            print(label)
        elif self.is_bookmark_chosen == True:
            self.cursor.execute(
                f"INSERT INTO past_reading_progress (bookmark, pdf_path,last_page_index,audio_path,last_time) \
                VALUES (?,?,?,?,?);",
                (
                    bookmark,
                    self.chosen_pdf.get(),
                    stop_page_index,
                    self.generated_audio_file.get(),
                    stop_time,
                ),
            )
            self.is_bookmark_chosen = False
            self.db.commit()
            label = "Data saved"
            print(label)

        if self.page_entry:
            self.page_entry.clear_entry()
        if self.timestamp_entry:
            self.timestamp_entry.clear_entry()
        self.title_4_label = tk.Label(self, text=label)
        self.title_4_label.grid(row=self.row_number, column=0, sticky="W", columnspan=2)
        self._increment_row_number()

        self._reconfigure_column_space()

    def get_saved_data(self):
        pdf_path = self.chosen_pdf.get()
        self.cursor.execute(
            "SELECT * FROM past_reading_progress WHERE pdf_path = ?", (pdf_path,)
        )
        rows = self.cursor.fetchall()
        sorted_result = []
        for row in sorted(rows, key=lambda n: int(n["last_page_index"])):
            sorted_result.append(
                row["bookmark"] + " at page " + str(row["last_page_index"] + 1)
            )
        return sorted_result

    def load_past_data(self, past_data_bookmark):
        pdf_path = self.chosen_pdf.get()
        self.cursor.execute(
            "SELECT * FROM past_reading_progress WHERE pdf_path = ? AND bookmark = ?",
            (pdf_path, past_data_bookmark),
        )
        return self.cursor.fetchall()


# # Fetch all the rows returned by the query
# rows = cursor.fetchall()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("App Window")
    target_width = int(SCREEN_WIDTH * 0.3)
    target_height = int(SCREEN_HEIGHT * 0.7)
    root.geometry(f"{target_width}x{target_height}")

    nv = PDFNavigator(root)
    nv.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    def resize_frame(event):
        nv.grid_propagate(0)

    root.bind("<Configure>", resize_frame)

    root.mainloop()
