import asyncio
from unittest import mock

import pytest

from ObjectHandlers.audio_handler import AudioHandler, TimeStamp


def test_audio_opener_that_accept_non_audio_file_extension_raises_ValueError():
    with pytest.raises(ValueError):
        AudioHandler("dwad")
    with pytest.raises(ValueError):
        AudioHandler("dwad.txt")


@mock.patch("ObjectHandlers.audio_handler.asyncio.create_subprocess_shell")
@mock.patch("ObjectHandlers.audio_handler.pygetwindow.getWindowsWithTitle")
@mock.patch("asyncio.sleep")
def test_first_time_opening_audio(mock_sleep, mock_get_windows, mock_call):
    # Arange
    mock_get_windows.return_value = [mock.MagicMock()]

    async def async_mock(*args, **kwargs):
        return True

    audio_opener = AudioHandler("test.wav")
    timestamp = TimeStamp(stamp="00:40:00")

    with mock.patch.object(AudioHandler, "wait_for_window", async_mock):
        # Act
        asyncio.run(audio_opener.open_audio_file(timestamp))

        # Assert
        mock_call.assert_called_once_with(
            " ".join(
                [
                    "vlc",
                    '"test.wav"',
                    "--start-time",
                    str(40 * 60),
                ]
            )
        )
