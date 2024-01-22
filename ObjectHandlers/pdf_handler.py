import asyncio

import pygetwindow
from pypdf import PdfReader

from Components.const import *

# from asyncio.subprocess import PIPE


class PDFSection:
    def __init__(
        self,
        bookmark,
        *,
        start_stop_index=None,
        start_stop_page=None,
    ) -> None:
        self.bookmark = bookmark
        if start_stop_index is not None:
            self._start_index, self._stop_index = start_stop_index
        elif start_stop_page is not None:
            self._start_index, self._stop_index = start_stop_page
            self._start_index -= 1
            self._stop_index -= 1

    def __str__(self) -> str:
        return f"{self.bookmark} at page {self.start_page}"

    @property
    def start_page(self):
        return self._start_index + 1

    @start_page.setter
    def start_index(self, value):
        self._start_index = value - 1

    @property
    def stop_page(self):
        return self._stop_index + 1

    @property
    def start_index(self):
        return self._start_index

    @start_index.setter
    def start_index(self, value):
        self._start_index = value

    @property
    def stop_index(self):
        return self._stop_index


class PDFHandler:
    def __init__(self, filename) -> None:
        self.set_filename(filename)
        self.is_opened = False

    def set_filename(self, filename):
        if filename.endswith(".pdf"):
            self.filename = filename
            self.pdf_reader = PdfReader(filename)
        else:
            raise ValueError("Wrong file type.")

    def get_sorted_section_list(self):
        return [
            self.get_section_from_bookmark(bookmark)
            for bookmark in self._get_sorted_bookmark_list()
        ]

    def get_section_from_bookmark(self, bookmark):
        bookmark_to_page_dict = self._get_bookmark_to_page_dict()
        start_page_index = bookmark_to_page_dict.get(bookmark)
        bookmark_pages_list = self._get_sorted_bookmark_list()
        stop_page_index = start_page_index
        extra_index = 0
        while start_page_index is not None and start_page_index == stop_page_index:
            try:
                next_bookmark = bookmark_pages_list[
                    bookmark_pages_list.index(bookmark) + 1 + extra_index
                ]
            except IndexError:
                stop_page_index = len(
                    self.pdf_reader.pages
                )  # this will always be bigger than page index
            else:
                stop_page_index = bookmark_to_page_dict[next_bookmark]

            extra_index += 1

        return PDFSection(
            bookmark=bookmark, start_stop_index=(start_page_index, stop_page_index)
        )

    async def wait_for_window(
        self, title, check_function, timeout=10, polling_interval=0.5
    ):
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            if check_function(title):
                return True
            await asyncio.sleep(polling_interval)
        return False

    def is_window_open(self, title):
        return bool(pygetwindow.getWindowsWithTitle(title))

    # Default check function for window closed
    def is_window_closed(self, title):
        return not bool(pygetwindow.getWindowsWithTitle(title))

    async def open_pdf_at(self, section: PDFSection):
        page = section.start_page
        if self.is_opened:
            command = [
                "sumatrapdf",
                "-reuse-instance",
                "-page",
                str(page),
                self.filename,
            ]
        else:
            command = [
                "sumatrapdf",
                "-page",
                str(page),
                self.filename,
            ]
            self.is_opened = True

        await asyncio.create_subprocess_exec(*command)
        window_open = await self.wait_for_window("SumatraPDF", self.is_window_open)
        if window_open:
            print(f"Window for '{command}' is open.")
        else:
            raise TimeoutError("SumatraPDF takes too long to open")

        # adjust window
        pdf_reader_window = pygetwindow.getWindowsWithTitle("SumatraPDF")[0]
        x_offset = -7
        y_offset = 0
        y_size_offset = 6
        pdf_reader_window.moveTo(x_offset, y_offset)
        pdf_reader_window.resizeTo(
            int(SCREEN_WIDTH * 0.7), SCREEN_HEIGHT + y_size_offset
        )

    def extract_text(self, pdf_section: PDFSection):
        start_page = pdf_section.start_index
        stop_page = pdf_section.stop_index
        if stop_page is None:
            stop_page = start_page + 1
        parts = []

        def visitor_body(text, cm, tm, font_dict, font_size):
            y = tm[5]
            if y > 45 and y < 815:
                parts.append(text)

        for page_index in range(start_page, stop_page):
            page = self.pdf_reader.pages[page_index]
            page.extract_text(visitor_text=visitor_body)
        text_body = "".join(parts)

        return text_body

    def _get_sorted_bookmark_list(self):
        bookmark_to_page_dict = self._get_bookmark_to_page_dict()
        sorted_result = []
        for bookmark, _ in sorted(
            bookmark_to_page_dict.items(), key=lambda n: int(n[1])
        ):
            sorted_result.append(bookmark)
        return sorted_result

    def _get_bookmark_to_page_dict_recursive(self, bookmark_list):
        result = {}
        for item in bookmark_list:
            if isinstance(item, list):
                # continue
                result.update(self._get_bookmark_to_page_dict_recursive(item))
            else:
                page_index = self.pdf_reader.get_destination_page_number(item)
                result[item.title] = page_index  # title here is the bookmark name

        if not result:
            result = {"page 1": 0}
        return result

    def _get_bookmark_to_page_dict(self):
        return self._get_bookmark_to_page_dict_recursive(self.pdf_reader.outline)


if __name__ == "__main__":
    file_path = "../../../Desktop/Game Programming Patterns.pdf"
    popener = PDFHandler(file_path)

    print(popener._get_sorted_bookmark_list())

    # popener.open_pdf_with_sumatrapdf(100)
    # open_pdf_with_default_app(file_path)
    # popener.open_pdf_with_sumatrapdf(20)

    # p2t = Pdf2Text(file_path=file_path)

    # text_body = pop.extract_text(116, 132)

    # print(sys.getsizeof(text_body))

    # output_file = "extracted_text.txt"
    # with open(output_file, "w", encoding="utf-8") as file:
    #     file.write(text_body)
