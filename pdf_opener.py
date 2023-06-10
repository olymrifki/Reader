import subprocess


class PDFOpener:
    def __init__(self, pdf_path: str) -> None:
        self.is_opened = False
        if pdf_path.endswith(".pdf"):
            self.pdf_path = pdf_path
        else:
            raise ValueError("Wrong file type.")

    def open_pdf_with_sumatrapdf(
        self,
        page_number=1,
    ):
        # Construct the command to open the PDF at the specific page
        if self.is_opened:
            command = [
                "sumatrapdf",
                "-reuse-instance",
                "-page",
                str(page_number),
                self.pdf_path,
            ]
        else:
            command = [
                "sumatrapdf",
                "-page",
                str(page_number),
                self.pdf_path,
            ]
            self.is_opened = True
        subprocess.Popen(command)


if __name__ == "__main__":
    file_path = "../../../Desktop/Game Programming Patterns.pdf"
    popener = PDFOpener(file_path)
    popener.open_pdf_with_sumatrapdf(100)
    # open_pdf_with_default_app(file_path)
    popener.open_pdf_with_sumatrapdf(20)
