from unittest import mock

import pytest

from audio_opener import AudioOpener


def test_audio_opener_that_accept_non_audio_file_extension_raises_ValueError():
    with pytest.raises(ValueError):
        AudioOpener("dwad")
    with pytest.raises(ValueError):
        AudioOpener("dwad.txt")


@mock.patch("audio_opener.subprocess.Popen")
def test_first_time_opening_audio(mock_Popen):
    # Arange
    audio_opener = AudioOpener("test.wav")

    # Acv
    audio_opener.open_file_with_potplayer("00:40:00")

    # Assert
    mock_Popen.assert_called_once_with(
        [
            "PotPlayerMini",
            "test.wav",
            "/new",
            "/seek=00:40:00",
        ]
    )
