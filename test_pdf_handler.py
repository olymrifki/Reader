import subprocess
import time
from unittest import mock

import pygetwindow as gw
import pytest

# import pdf_handler
from pdf_handler import PDFHandler, PDFSection


def test_pdf_handler_accept_non_pdf_file_extension():
    with pytest.raises(ValueError):
        PDFHandler("dwad")
    with pytest.raises(ValueError):
        PDFHandler("dwad.txt")


@mock.patch("pdf_handler.PdfReader")
@mock.patch("subprocess.Popen")
def test_first_time_opening_pdf(mock_call, mock_reader):
    pdf_handler = PDFHandler("test.pdf")
    section = PDFSection(bookmark="test", start_stop_page=(100, 200))

    pdf_handler.open_pdf_with_sumatrapdf_at(section)

    mock_call.assert_called_once_with(
        [
            "sumatrapdf",
            "-page",
            "100",
            "test.pdf",
        ]
    )
    assert pdf_handler.is_opened is True


@mock.patch("pdf_handler.PdfReader")
@mock.patch("subprocess.Popen")
def test_second_time_opening_pdf(mock_call, mock_reader):
    pdf_handler = PDFHandler("test.pdf")
    section1 = PDFSection(bookmark="test", start_stop_page=(100, 200))
    section2 = PDFSection(bookmark="test", start_stop_page=(20, 100))

    pdf_handler.open_pdf_with_sumatrapdf_at(section1)
    pdf_handler.open_pdf_with_sumatrapdf_at(section2)

    assert mock_call.call_args[0][0] == [
        "sumatrapdf",
        "-reuse-instance",
        "-page",
        "20",
        "test.pdf",
    ]
