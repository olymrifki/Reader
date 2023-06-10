import sys

from pypdf import PdfReader


class Pdf2Text:
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.reader = PdfReader(file_path)

    def extract_text(self, start_page, stop_page=None):
        if stop_page is None:
            stop_page = start_page + 1
        parts = []

        def visitor_body(text, cm, tm, font_dict, font_size):
            y = tm[5]
            if y > 45 and y < 815:
                parts.append(text)

        for page_index in range(start_page, stop_page):
            page = self.reader.pages[page_index]
            page.extract_text(visitor_text=visitor_body)
        text_body = "".join(parts)

        return text_body


if __name__ == "__main__":
    file_path = "../../../Desktop/Game Programming Patterns.pdf"
    p2t = Pdf2Text(file_path=file_path)

    text_body = p2t.extract_text(116, 132)

    print(sys.getsizeof(text_body))

    output_file = "extracted_text.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text_body)
