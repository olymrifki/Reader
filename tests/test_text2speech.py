import sys
import time
import wave
from unittest import mock

import pytest
from requests.exceptions import HTTPError

sys.path.append("..")
from ObjectHandlers.audio_handler import AudioHandler


def test_make_request_success():
    # Create an instance of the class
    tts = AudioHandler("./tes.wav")

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.content = b"mock_audio_content"

    # Patch requests.post to return the mock response
    with mock.patch("requests.post", return_value=mock_response) as mock_post:
        # Call the make_request method
        result = tts._make_request("some text")

        # Assertions
        mock_post.assert_called_once_with(
            tts.url,
            data={
                "key": tts.key_code,
                "src": "some text",
                "hl": tts.hl,
                "v": tts.voice,
            },
        )
        assert result == b"mock_audio_content"


def test_make_request_http_error():
    # Create an instance of the class
    tts = AudioHandler("./tes.wav")

    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError("Mock HTTP error")

    # Patch requests.post to return the mock response
    with mock.patch("requests.post", return_value=mock_response) as mock_post:
        # Call the make_request method and assert that it raises the expected exception
        with pytest.raises(HTTPError):
            tts._make_request("some text")

        # Assertion
        mock_post.assert_called_once_with(
            tts.url,
            data={
                "key": tts.key_code,
                "src": "some text",
                "hl": tts.hl,
                "v": tts.voice,
            },
        )


def test_small_text_after_strip_pass_check_test():
    # Create an instance of the class
    tts = AudioHandler("./tes.wav")

    result = tts._check_text("some\ntext")
    assert result == "some text"


def test_text_is_too_big():
    # Create an instance of the class
    tts = AudioHandler("./tes.wav")

    with mock.patch("sys.getsizeof", return_value=100_000) as mock_getsizeof:
        # Call the make_request method
        with pytest.raises(MemoryError):
            result = tts._check_text("some text")
        mock_getsizeof.assert_called_once_with("some text")


@mock.patch("audio_handler.requests.post")
@mock.patch.object(wave, "open")
@mock.patch.object(time, "sleep")
def test_success_convertion_requests_the_text_and_save_the_response_to_sound_file(
    mock_sleep, mock_wave_open, mock_request_post
):
    # Arange
    tts = AudioHandler("./tes.wav")

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.content = b"mock_audio_content"
    mock_request_post.return_value = mock_response

    mock_writeframes = mock.Mock()
    mock_wave_open.return_value.__enter__.return_value.writeframes = mock_writeframes

    # Act
    tts.convert("some text")

    # Assert
    mock_request_post.assert_called_once_with(
        tts.url,
        data={
            "key": tts.key_code,
            "src": "some text",
            "hl": tts.hl,
            "v": tts.voice,
        },
    )
    mock_wave_open.assert_called_once_with("./tes.wav", "wb")
    mock_writeframes.assert_called_once_with(mock_response.content)
