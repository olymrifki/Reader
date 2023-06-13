from unittest import mock

import pytest

from audio_handler import AudioHandler, TimeStamp


def test_audio_opener_that_accept_non_audio_file_extension_raises_ValueError():
    with pytest.raises(ValueError):
        AudioHandler("dwad")
    with pytest.raises(ValueError):
        AudioHandler("dwad.txt")


@mock.patch("audio_handler.subprocess.Popen")
def test_first_time_opening_audio(mock_Popen):
    # Arange
    audio_opener = AudioHandler("test.wav")
    timestamp = TimeStamp(stamp="00:40:00")

    # Acv
    audio_opener.open_file_with_potplayer(timestamp)

    # Assert
    mock_Popen.assert_called_once_with(
        [
            "PotPlayerMini",
            "test.wav",
            "/new",
            "/seek=00:40:00",
        ]
    )
