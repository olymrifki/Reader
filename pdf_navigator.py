import os
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, ttk

import pygetwindow as gw

from audio_handler import AudioHandler, TimeStamp
from Components.const import *
from Components.labelled_search_input import LabelledSearchInput
from Components.progress_deleter import ProgessDeleter
from Components.progress_loader import ProgessLoader
from Components.progress_saver import ProgessSaver
from Components.separator import Separator
from Components.starting import StartingGui
from db_handler import DBHandler, ReadingDataRow
from pdf_handler import PDFHandler, PDFSection

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
            self.pdf_filename = pdf_filename
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
        self.save_component.reempty_entries()

    def save_progress(self, page_entry, time_entry):
        print("getting data")
        stop_page_index = self._validate_page_input(page_entry)
        stop_time = self._validate_time_input(time_entry)
        if not stop_page_index or not stop_time:
            return

        print("data retrieved, saving...")
        if self.is_bookmark_chosen == True:
            data = ReadingDataRow(
                self.bookmark_choice.get(),
                self.pdf_filename,
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
                self.pdf_filename,
                stop_page_index,
                self.audio_handler.filename,
                stop_time,
            )
            self.db.update_data(data)
            label = "Data updated"
            print(label)

        self.main_gui.add_component(tk.Label(self.main_gui, text=label))

        self.past_progress = self._get_saved_data()
        self.saved_progress_menu.update_choices(new_choices=self.past_progress)
        self.delete_progress_menu.update_choices(new_choices=self.past_progress)

    def delete_bookmark(self):
        if self.past_progress_bookmark_choice.get() == "":
            return
        self._delete_past_data(self.past_progress_bookmark_choice.get())
        self.past_progress_bookmark_choice.set("")

        label = "Progress deleted"
        self.main_gui.add_component(tk.Label(self.main_gui, text=label))

        self.past_progress = self._get_saved_data()
        self.saved_progress_menu.update_choices(new_choices=self.past_progress)
        self.delete_progress_menu.update_choices(new_choices=self.past_progress)

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
            self.past_progress_pack = (
                self.past_progress_bookmark_choice,
                self.past_progress,
                self._past_progress_choice_changed,
            )

            progress_loader = ProgessLoader(
                bookmark, self.past_progress_pack, self.open_audio, self.main_gui
            )
            self.bookmark_menu = progress_loader.bookmark_menu
            self.saved_progress_menu = progress_loader.saved_progress_menu
            # Components
            self.main_gui.add_component(progress_loader)
            self.main_gui.add_component(Separator(self.main_gui))

        else:
            self.past_progress = self._get_saved_data()
            self.bookmark_pages_list = [
                str(section) for section in self.pdf_handler.get_sorted_section_list()
            ]
            self.bookmark_menu.update_choices(new_choices=self.bookmark_pages_list)
            self.saved_progress_menu.update_choices(new_choices=self.past_progress)

            self.bookmark_choice.set("")
            self.past_progress_bookmark_choice.set("")
        self.is_loader_loaded = True

    def _setup_saving_components(self):
        """Define and place tkinter components for saving progress loader application interface."""

        if not self.is_saving_loaded:
            # progress saver

            self.save_component = ProgessSaver(self.save_progress, self.main_gui)
            self.main_gui.add_component(self.save_component)
            self.main_gui.add_component(Separator(self.main_gui))

            # progress deleter
            progress_deleter = ProgessDeleter(
                self.delete_bookmark, self.past_progress_pack, self.main_gui
            )
            self.delete_progress_menu = progress_deleter.delete_progress_menu
            self.main_gui.add_component(progress_deleter)
            self.main_gui.add_component(Separator(self.main_gui))

        self.is_saving_loaded = True

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

    def _get_audio_file_name(self):
        filename_without_extension = os.path.splitext(
            os.path.basename(self.pdf_filename)
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

    def _get_saved_data(self):
        rows = self.db.read_data(self.db.filter_condition(pdf_path=self.pdf_filename))
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
                bookmark=past_data_bookmark, pdf_path=self.pdf_filename
            )
        )

    def _load_past_data(self, past_data_bookmark):
        print(f"\n\n{past_data_bookmark}\n\n")
        return self.db.read_data(
            self.db.filter_condition(
                bookmark=past_data_bookmark, pdf_path=self.pdf_filename
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
