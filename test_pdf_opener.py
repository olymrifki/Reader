from unittest.mock import patch

import pytest

from pdf_opener import PDFOpener


def test_pdf_opener_accept_non_pdf_file_extension():
    with pytest.raises(ValueError):
        PDFOpener("dwad")
    with pytest.raises(ValueError):
        PDFOpener("dwad.txt")


def test_first_time_opening_pdf():
    pdf_opener = PDFOpener("test.pdf")

    with patch("subprocess.Popen") as mock_call:
        pdf_opener.open_pdf_with_sumatrapdf(100)
        # print(mock_call.call_args[0][0])
        mock_call.assert_called_once_with(
            [
                "sumatrapdf",
                "-page",
                "100",
                "test.pdf",
            ]
        )
        assert pdf_opener.is_opened is True


def test_second_time_opening_pdf():
    pdf_opener = PDFOpener("test.pdf")

    with patch("subprocess.Popen") as mock_call:
        pdf_opener.open_pdf_with_sumatrapdf(100)
        pdf_opener.open_pdf_with_sumatrapdf(20)

        assert mock_call.call_args[0][0] == [
            "sumatrapdf",
            "-reuse-instance",
            "-page",
            "20",
            "test.pdf",
        ]
