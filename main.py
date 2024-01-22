import asyncio
import os
import threading
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
        filetypes = (("PDF Files", "*.pdf"),)
        pdf_filename = filedialog.askopenfile(mode="r", filetypes=filetypes).name
        self.search_pdf.path_entry.delete(0, tk.END)
        self.search_pdf.path_entry.insert(tk.END, pdf_filename)
        if pdf_filename.endswith(".pdf"):
            self.pdf_filename = pdf_filename
            self.pdf_handler = PDFHandler(pdf_filename)

            if not self.is_loader_loaded:
                self._setup_loader_components()
                self.is_loader_loaded = True
            else:
                self._reload_loader_components()

    def open_pdf_page_and_audio(self):
        async def asyncfunc():
            await self._open_pdf_page_and_audio()

        asyncio.run(asyncfunc())

    async def _open_pdf_page_and_audio(self):
        filename_without_extension = os.path.splitext(
            os.path.basename(self.pdf_filename)
        )[0]
        audio_filename = (
            self.audio_directory
            + filename_without_extension
            + "_"
            + str(self.pdf_section.start_page)
            + "-"
            + str(self.pdf_section.stop_page)
            + ".wav"
        )
        self.audio_handler = AudioHandler(filename=audio_filename)
        if self.is_bookmark_chosen == True:
            start_time = TimeStamp(seconds=0)
            #
            text = self.pdf_handler.extract_text(self.pdf_section)
            self.audio_handler.convert(text)

        elif self.is_bookmark_chosen == False:
            past_data = self.db.read_data(
                self.db.filter_condition(
                    bookmark=self.past_progress_bookmark_choice.get(),
                    pdf_path=self.pdf_filename,
                )
            )[0]
            start_time = TimeStamp(stamp=past_data["last_time"])
            self.pdf_section.start_index = int(past_data["last_page_index"])
            self.audio_handler.set_file(past_data["audio_path"])

        await asyncio.gather(
            self.audio_handler.open_audio_file(start_time),
            self.pdf_handler.open_pdf_at(section=self.pdf_section),
        )

        self._setup_saving_components()
        start_page_index = self.pdf_section.start_index
        stop_page_index = self.pdf_section.stop_index
        self.save_component.reempty_entries(
            str(self.audio_handler.duration()), start_page_index, stop_page_index
        )

    def save_progress(self, stop_page_index, stop_time):
        if not stop_page_index or not stop_time:
            return

        if self.is_bookmark_chosen == True:
            bookmark_choice = self.bookmark_choice.get()
            db_function = self.db.create_data
            label = "Data saved"
            self.past_progress_bookmark_choice.set(self.bookmark_choice.get())
            self.bookmark_choice.set("")
            self.is_bookmark_chosen = False

        elif self.is_bookmark_chosen == False:
            bookmark_choice = self.past_progress_bookmark_choice.get()
            db_function = self.db.update_data
            label = "Data updated"

        data = ReadingDataRow(
            bookmark_choice,
            self.pdf_filename,
            stop_page_index,
            self.audio_handler.filename,
            stop_time,
        )
        db_function(data)
        print(label)

        self.main_gui.add_component(tk.Label(self.main_gui, text=label))

        self.past_progress = self._load_past_progress()
        self.saved_progress_menu.update_choices(new_choices=self.past_progress)
        self.delete_progress_menu.update_choices(new_choices=self.past_progress)

    def delete_bookmark(self):
        if self.past_progress_bookmark_choice.get() == "":
            return
        self.db.delete_data(
            self.db.filter_condition(
                bookmark=self.past_progress_bookmark_choice.get(),
                pdf_path=self.pdf_filename,
            )
        )
        self.past_progress_bookmark_choice.set("")

        label = "Progress deleted"
        self.main_gui.add_component(tk.Label(self.main_gui, text=label))

        self.past_progress = self._load_past_progress()
        self.saved_progress_menu.update_choices(new_choices=self.past_progress)
        self.delete_progress_menu.update_choices(new_choices=self.past_progress)

    def _setup_loader_components(self):
        """Define and place tkinter components for book section loader application interface."""

        tk_window = gw.getWindowsWithTitle("App Window")[0]
        x_offset = -23
        tk_window.moveTo(int(SCREEN_WIDTH * 0.7) + x_offset, 0)

        self.bookmark_pages_list = [
            str(section) for section in self.pdf_handler.get_sorted_section_list()
        ]
        self.past_progress = self._load_past_progress()
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
            bookmark,
            self.past_progress_pack,
            self.open_pdf_page_and_audio,
            self.main_gui,
        )
        self.bookmark_menu = progress_loader.bookmark_menu
        self.saved_progress_menu = progress_loader.saved_progress_menu
        # Components
        self.main_gui.add_component(progress_loader)
        self.main_gui.add_component(Separator(self.main_gui))

    def _reload_loader_components(self):
        self.past_progress = self._load_past_progress()
        self.bookmark_pages_list = [
            str(section) for section in self.pdf_handler.get_sorted_section_list()
        ]
        self.bookmark_menu.update_choices(new_choices=self.bookmark_pages_list)
        self.saved_progress_menu.update_choices(new_choices=self.past_progress)

        self.bookmark_choice.set("")
        self.past_progress_bookmark_choice.set("")

    def _setup_saving_components(self):
        """Define and place tkinter components for saving progress loader application interface."""

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

    def _load_past_progress(self):
        rows = self.db.read_data(self.db.filter_condition(pdf_path=self.pdf_filename))
        sorted_result = []
        for row in sorted(rows, key=lambda n: int(n["last_page_index"])):
            sorted_result.append(
                row["bookmark"] + " at page " + str(row["last_page_index"] + 1)
            )
        if not sorted_result:
            sorted_result.append("No Bookmark")
        return sorted_result


if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF to Audio App")
    x_offset = 23
    target_width = int(SCREEN_WIDTH * 0.3) + x_offset
    target_height = int(SCREEN_HEIGHT * 0.7)
    root.geometry(f"{target_width}x{target_height}")

    nv = PDFNavigator(root)
    nv.pack(fill="both", expand=1)

    root.mainloop()
    nv.db.db.close()
