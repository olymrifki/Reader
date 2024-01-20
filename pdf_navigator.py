import os
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, ttk

import pygetwindow as gw

from audio_handler import AudioHandler, TimeStamp
from Components.const import *
from Components.labelled_search_input import LabelledSearchInput
from Components.progress_loader import ProgessLoader
from Components.separator import Separator
from Components.starting import StartingGui
from db_handler import DBHandler, ReadingDataRow
from pdf_handler import PDFHandler, PDFSection
from placeholder_entry import PlaceholderEntry

# SCREEN_WIDTH


class PDFNavigator(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DBHandler()

        self.is_bookmark_chosen = False

        self.configure(background="black")
        self.is_loader_loaded = False
        self.is_saving_loaded = False
        self.row_number = 0
        self.audio_directory = "D:/requested_audios/"

        self.main_gui = StartingGui(self)
        self.search_pdf = LabelledSearchInput(
            self.input_and_start_PDFreader, self.main_gui
        )
        self.main_gui.add_component(self.search_pdf)
        self.main_gui.add_component(Separator(self.main_gui))

        self.main_gui.pack(fill="both", expand=1, padx=10, pady=10)

    def input_and_start_PDFreader(self):
        """Callback for Get PDF button"""
        pdf_filename = self._input_pdf_filename()
        if pdf_filename.endswith(".pdf"):
            self.pdf_handler = PDFHandler(pdf_filename)
            self._setup_loader_components()

    def open_audio(self):
        self.audio_handler = AudioHandler(filename=self._get_audio_file_name())
        if self.is_bookmark_chosen == True:
            start_time = TimeStamp(seconds=0)
            #
            text = self.pdf_handler.extract_text(self.pdf_section)
            self.audio_handler.convert(text)

        elif self.is_bookmark_chosen == False:
            past_data = self._load_past_data(self.past_progress_bookmark_choice.get())[
                0
            ]
            start_time = TimeStamp(stamp=past_data["last_time"])
            # additional
            self.pdf_section.start_index = int(past_data["last_page_index"])
            self.audio_handler.set_file(past_data["audio_path"])

        self._open_pdf_app()
        self._open_audio_app(start_at=start_time)

        self._setup_saving_components()
        self._reempty_entries()

    def save_progress(self):
        print("getting data")
        stop_page_index = self._validate_page_input(self.page_entry.get())
        stop_time = self._validate_time_input(self.timestamp_entry.get())
        if not stop_page_index or not stop_time:
            return

        print("data retrieved, saving...")
        if self.is_bookmark_chosen == True:
            data = ReadingDataRow(
                self.bookmark_choice.get(),
                self.pdf_handler.filename,
                stop_page_index,
                self.audio_handler.filename,
                stop_time,
            )
            self.db.create_data(data)
            self.past_progress_bookmark_choice.set(self.bookmark_choice.get())
            self.bookmark_choice.set("")
            self.is_bookmark_chosen = False
            label = "Data saved"
            print(label)
        elif self.is_bookmark_chosen == False:
            data = ReadingDataRow(
                self.past_progress_bookmark_choice.get(),
                self.pdf_handler.filename,
                stop_page_index,
                self.audio_handler.filename,
                stop_time,
            )
            self.db.update_data(data)
            label = "Data updated"
            print(label)

        if self.page_entry:
            self.page_entry.clear_entry()
        if self.timestamp_entry:
            self.timestamp_entry.clear_entry()
        self.title_5_label = tk.Label(self, text=label)
        self.title_5_label.grid(row=self.row_number, column=0, sticky="W", columnspan=2)
        self._increment_row_number()
        self.past_progress = self._get_saved_data()
        self._update_choices(
            menu=self.progress_menu["menu"],
            menu_var=self.past_progress_bookmark_choice,
            new_choices=self.past_progress,
            after_command=self._past_progress_choice_changed,
        )
        self._update_choices(
            menu=self.progress_menu_copy["menu"],
            menu_var=self.past_progress_bookmark_choice,
            new_choices=self.past_progress,
            after_command=self._past_progress_choice_changed,
        )
        self._reconfigure_column_space()

    def delete_bookmark(self):
        if self.past_progress_bookmark_choice.get() == "":
            return
        self._delete_past_data(self.past_progress_bookmark_choice.get())
        self.past_progress_bookmark_choice.set("")
        label = "Progress deleted"
        self.title_5_label = tk.Label(self, text=label)
        self.title_5_label.grid(row=self.row_number, column=0, sticky="W", columnspan=2)
        self._increment_row_number()
        self.past_progress = self._get_saved_data()
        self._update_choices(
            menu=self.progress_menu["menu"],
            menu_var=self.past_progress_bookmark_choice,
            new_choices=self.past_progress,
            after_command=self._past_progress_choice_changed,
        )
        self._update_choices(
            menu=self.progress_menu_copy["menu"],
            menu_var=self.past_progress_bookmark_choice,
            new_choices=self.past_progress,
            after_command=self._past_progress_choice_changed,
        )
        self._reconfigure_column_space()

    def _increment_row_number(self):
        self.row_number += 1

    def _setup_loader_components(self):
        """Define and place tkinter components for book section loader application interface."""

        if not self.is_loader_loaded:
            tk_window = gw.getWindowsWithTitle("App Window")[0]
            x_offset = -23
            tk_window.moveTo(int(SCREEN_WIDTH * 0.7) + x_offset, 0)

            self.bookmark_pages_list = [
                str(section) for section in self.pdf_handler.get_sorted_section_list()
            ]
            self.past_progress = self._get_saved_data()
            self.bookmark_choice = tk.StringVar()
            self.past_progress_bookmark_choice = tk.StringVar()

            bookmark = (
                self.bookmark_choice,
                self.bookmark_pages_list,
                self._bookmark_choice_changed,
            )
            past_progress = (
                self.past_progress_bookmark_choice,
                self.past_progress,
                self._past_progress_choice_changed,
            )
            # Components
            self.main_gui.add_component(
                ProgessLoader(bookmark, past_progress, self.open_audio, self.main_gui)
            )
            self.main_gui.add_component(Separator(self.main_gui))

        else:
            self.past_progress = self._get_saved_data()
            self.bookmark_pages_list = [
                str(section) for section in self.pdf_handler.get_sorted_section_list()
            ]
            self._update_choices(
                menu=self.menu["menu"],
                menu_var=self.bookmark_choice,
                new_choices=self.bookmark_pages_list,
                after_command=self._bookmark_choice_changed,
            )
            self._update_choices(
                menu=self.progress_menu["menu"],
                menu_var=self.past_progress_bookmark_choice,
                new_choices=self.past_progress,
                after_command=self._past_progress_choice_changed,
            )
            self.bookmark_choice.set("")
            self.past_progress_bookmark_choice.set("")
        self.is_loader_loaded = True

    def _setup_saving_components(self):
        """Define and place tkinter components for saving progress loader application interface."""

        if not self.is_saving_loaded:
            page_entry_placeholder = ""
            timestamp_entry_placeholder = ""

            # Components
            self.title_3_label = tk.Label(self.main_gui, text="Save Progress: ")
            self.save_page_label = tk.Label(self.main_gui, text="Page to save: ")
            self.page_entry = PlaceholderEntry(
                self.main_gui, placeholder_text=page_entry_placeholder
            )
            self.save_timestamp_label = tk.Label(
                self.main_gui, text="Timestamp to save: "
            )
            self.timestamp_entry = PlaceholderEntry(
                self.main_gui, placeholder_text=timestamp_entry_placeholder
            )
            self.save_progress_button = tk.Button(
                self.main_gui, text="Save this progress", command=self.save_progress
            )
            self.separator_frame3 = tk.Frame(
                self.main_gui, height=2, bd=1, relief=tk.SUNKEN
            )
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

            # Components
            self.title_4_label = tk.Label(
                self, text="Finish Reading? Delete the Progress: "
            )
            self.delete_bookmark_label = tk.Label(self, text="Progress to delete: ")
            self.progress_menu_copy = tk.OptionMenu(
                self,
                self.past_progress_bookmark_choice,
                *self.past_progress,
                command=self._past_progress_choice_changed,
            )
            self.delete_a_bookmark_button = tk.Button(
                self, text="Delete bookmark", command=self.delete_bookmark
            )

            # Placements
            self.title_4_label.grid(
                row=self.row_number, column=0, sticky="W", columnspan=2
            )
            self._increment_row_number()
            self.delete_bookmark_label.grid(column=0, row=self.row_number, sticky="W")
            self.progress_menu_copy.grid(column=1, row=self.row_number, sticky="W")
            self._increment_row_number()
            self.delete_a_bookmark_button.grid(
                padx=5, column=0, row=self.row_number, columnspan=2, sticky="W"
            )

            self.main_gui.add_component(Separator(self.main_gui))

        self.is_saving_loaded = True

    def _reconfigure_column_space(self):
        for col in range(self.grid_size()[0]):
            self.grid_columnconfigure(col, weight=1)

    def _input_pdf_filename(self):
        """Use tkinter filedialog to browse folder structures and"""
        filetypes = (("PDF Files", "*.pdf"),)
        pdf_filename = filedialog.askopenfile(mode="r", filetypes=filetypes).name
        self.search_pdf.path_entry.delete(0, tk.END)
        self.search_pdf.path_entry.insert(tk.END, pdf_filename)
        return pdf_filename

    def _bookmark_choice_changed(self, *args):
        self.is_bookmark_chosen = True
        self.past_progress_bookmark_choice.set("")
        self.bookmark_choice.set(self.bookmark_choice.get().split(" at page ")[0])
        print(f"\n\n{self.bookmark_choice.get()}\n\n")
        self.pdf_section = self.pdf_handler.get_section_from_bookmark(
            bookmark=self.bookmark_choice.get()
        )

    def _past_progress_choice_changed(self, *args):
        self.is_bookmark_chosen = False
        self.bookmark_choice.set("")
        self.past_progress_bookmark_choice.set(
            self.past_progress_bookmark_choice.get().split(" at page ")[0]
        )
        print(f"\n\n{self.past_progress_bookmark_choice.get()}\n\n")
        self.pdf_section = self.pdf_handler.get_section_from_bookmark(
            bookmark=self.past_progress_bookmark_choice.get()
        )

    def _open_pdf_app(self):
        self.pdf_handler.open_pdf_with_sumatrapdf_at(section=self.pdf_section)

        while not gw.getWindowsWithTitle("SumatraPDF"):
            time.sleep(0.1)
        time.sleep(0.5)
        pdf_reader_window = gw.getWindowsWithTitle("SumatraPDF")[0]
        x_offset = -7
        y_offset = 0
        y_size_offset = 6
        pdf_reader_window.moveTo(x_offset, y_offset)
        pdf_reader_window.resizeTo(
            int(SCREEN_WIDTH * 0.7), SCREEN_HEIGHT + y_size_offset
        )

    # refactored up to here

    def _reempty_entries(self):
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

    def _get_audio_file_name(self):
        filename_without_extension = os.path.splitext(
            os.path.basename(self.pdf_handler.filename)
        )[0]
        return (
            self.audio_directory
            + filename_without_extension
            + "_"
            + str(self.pdf_section.start_page)
            + "-"
            + str(self.pdf_section.stop_page)
            + ".wav"
        )

    def _open_audio_app(self, start_at: TimeStamp = TimeStamp(seconds=0)):
        start_at = str(start_at)
        print(f"\n\n{start_at}\n\n")
        for sound_player_window in gw.getWindowsWithTitle("PotPlayer"):
            sound_player_window.close()

        if start_at is None:
            self.audio_handler.open_file_with_potplayer()
        else:
            self.audio_handler.open_file_with_potplayer(start_at)
            print(f"\n\ndddd{start_at}\n\n")
        while not gw.getWindowsWithTitle("PotPlayer"):
            time.sleep(0.1)
        time.sleep(3)
        x_offset = -15
        x_size_offset = 17
        sound_player_window = gw.getWindowsWithTitle("PotPlayer")[0]
        sound_player_window.moveTo(
            int(SCREEN_WIDTH * 0.7) + x_offset, int(SCREEN_HEIGHT * 0.7)
        )
        sound_player_window.resizeTo(
            int(SCREEN_WIDTH * 0.3) + x_size_offset, int(SCREEN_HEIGHT * 0.3)
        )

    def _validate_time_input(self, time_input):
        time_input = TimeStamp(stamp=time_input)
        if not (
            time_input.seconds_value() > 0
            and time_input.seconds_value()
            < self.audio_handler.duration().seconds_value()
        ):
            return
        return str(time_input)

    def _validate_page_input(self, stop_page_input):
        stop_page_index_input = int(stop_page_input) - 1

        if not (
            stop_page_index_input >= self.pdf_section.start_index
            and stop_page_index_input < self.pdf_section.stop_index
        ):
            return
        return stop_page_index_input

    def _update_choices(self, menu, menu_var, new_choices, after_command):
        menu.delete(0, "end")
        for choice in new_choices:

            def func(value=choice):
                menu_var.set(value)
                after_command()

            menu.add_command(label=choice, command=func)

    def _get_saved_data(self):
        rows = self.db.read_data(
            self.db.filter_condition(pdf_path=self.pdf_handler.filename)
        )
        sorted_result = []
        for row in sorted(rows, key=lambda n: int(n["last_page_index"])):
            sorted_result.append(
                row["bookmark"] + " at page " + str(row["last_page_index"] + 1)
            )
        if not sorted_result:
            sorted_result.append("No Bookmark")
        return sorted_result

    def _delete_past_data(self, past_data_bookmark):
        print(f"\n\n{past_data_bookmark}\n\n")
        return self.db.delete_data(
            self.db.filter_condition(
                bookmark=past_data_bookmark, pdf_path=self.pdf_handler.filename
            )
        )

    def _load_past_data(self, past_data_bookmark):
        print(f"\n\n{past_data_bookmark}\n\n")
        return self.db.read_data(
            self.db.filter_condition(
                bookmark=past_data_bookmark, pdf_path=self.pdf_handler.filename
            )
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("App Window")
    x_offset = 23
    target_width = int(SCREEN_WIDTH * 0.3) + x_offset
    target_height = int(SCREEN_HEIGHT * 0.7)
    root.geometry(f"{target_width}x{target_height}")

    nv = PDFNavigator(root)
    nv.pack(fill="both", expand=1)
    # nv.grid(row=0, column=0, sticky="nsew")

    # root.grid_rowconfigure(0, weight=1)
    # root.grid_columnconfigure(0, weight=1)

    # def resize_frame(event):
    #     nv.grid_propagate(0)

    # root.bind("<Configure>", resize_frame)

    # def additional_code():
    # nv.db.close()

    # GUI setup code here

    # root.after(500, additional_code)
    root.mainloop()
    nv.db.db.close()
