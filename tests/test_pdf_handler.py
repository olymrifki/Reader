import asyncio
from unittest import mock

import pytest

from ObjectHandlers.pdf_handler import PDFHandler, PDFSection


def test_pdf_handler_accept_non_pdf_file_extension():
    with pytest.raises(ValueError):
        PDFHandler("dwad")
    with pytest.raises(ValueError):
        PDFHandler("dwad.txt")


@mock.patch("ObjectHandlers.pdf_handler.PdfReader")
@mock.patch("asyncio.create_subprocess_exec")
@mock.patch("ObjectHandlers.pdf_handler.pygetwindow.getWindowsWithTitle")
@mock.patch("asyncio.sleep")
def test_first_time_opening_pdf(mock_sleep, mock_get_windows, mock_call, mock_reader):
    mock_get_windows.return_value = [mock.MagicMock()]
    mock_reader.return_value = mock.MagicMock()

    async def async_mock(*args, **kwargs):
        return True

    section = PDFSection(bookmark="test", start_stop_page=(100, 200))
    pdf_handler = PDFHandler("test.pdf")

    with mock.patch.object(PDFHandler, "wait_for_window", async_mock):
        asyncio.run(pdf_handler.open_pdf_at(section))
        assert mock_call.call_args[0] == (
            "sumatrapdf",
            "-page",
            "100",
            "test.pdf",
        )

        assert pdf_handler.is_opened is True


@mock.patch("ObjectHandlers.pdf_handler.PdfReader")
@mock.patch("asyncio.create_subprocess_exec")
@mock.patch("ObjectHandlers.pdf_handler.pygetwindow.getWindowsWithTitle")
@mock.patch("asyncio.sleep")
def test_second_time_opening_pdf(mock_sleep, mock_get_windows, mock_call, mock_reader):
    mock_get_windows.return_value = [mock.MagicMock()]
    mock_reader.return_value = mock.MagicMock()
    pdf_handler = PDFHandler("test.pdf")
    section1 = PDFSection(bookmark="test", start_stop_page=(100, 200))
    section2 = PDFSection(bookmark="test", start_stop_page=(20, 100))

    async def async_mock(*args, **kwargs):
        return True

    with mock.patch.object(PDFHandler, "wait_for_window", async_mock):
        asyncio.run(pdf_handler.open_pdf_at(section1))
        asyncio.run(pdf_handler.open_pdf_at(section2))

        assert mock_call.call_args[0] == (
            "sumatrapdf",
            "-reuse-instance",
            "-page",
            "20",
            "test.pdf",
        )
