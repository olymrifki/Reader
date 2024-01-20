import subprocess

from pypdf import PdfReader

from Components.const import SCREEN_HEIGHT, SCREEN_WIDTH


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

    def open_pdf_with_sumatrapdf_at(self, section: PDFSection):
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
        subprocess.Popen(command)

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

    print(popener.get_sorted_bookmark_list())

    # popener.open_pdf_with_sumatrapdf(100)
    # open_pdf_with_default_app(file_path)
    # popener.open_pdf_with_sumatrapdf(20)

    # p2t = Pdf2Text(file_path=file_path)

    # text_body = pop.extract_text(116, 132)

    # print(sys.getsizeof(text_body))

    # output_file = "extracted_text.txt"
    # with open(output_file, "w", encoding="utf-8") as file:
    #     file.write(text_body)
