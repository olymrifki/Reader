import asyncio
import sys
import wave
from datetime import timedelta

import pygetwindow
import requests

from Components.const import *


# import time
class TimeStamp:
    def __init__(self, seconds: int = None, stamp: str = None) -> None:
        if seconds is not None:
            self._timestamp = timedelta(seconds=seconds)
        elif stamp is not None:
            self._timestamp = self._string_to_timedelta(stamp)
        else:
            raise ValueError("Provide time information")

    def __str__(self) -> str:
        total_seconds = self.seconds_value()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def value(self):
        return self._timestamp

    def seconds_value(self):
        return self._timestamp.total_seconds()

    def _timedelta_to_string(self, delta):
        total_seconds = delta.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def _string_to_timedelta(self, time_str):
        time_parts = time_str.split(":")
        if len(time_parts) == 3:
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = int(time_parts[2])
        elif len(time_parts) == 2:
            hours = 0
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])

        return timedelta(hours=hours, minutes=minutes, seconds=seconds)


class AudioHandler:
    def __init__(self, filename) -> None:
        self.set_file(filename)

    def set_file(self, filename):
        if filename.endswith(".wav") or filename.endswith(".mp3"):
            self.filename = filename
        else:
            raise ValueError("Wrong file type.")

    def duration(self):
        with wave.open(self.filename) as mywav:
            duration_seconds = mywav.getnframes() / mywav.getframerate()

        return TimeStamp(seconds=duration_seconds)

    async def wait_for_window(
        self, title, check_function, timeout=10, polling_interval=0.5
    ):
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            if check_function(title):
                return True
            await asyncio.sleep(polling_interval)
        return False

    def is_window_open(self, title):
        return bool(pygetwindow.getWindowsWithTitle(title))

    # Default check function for window closed
    def is_window_closed(self, title):
        return not bool(pygetwindow.getWindowsWithTitle(title))

    async def open_audio_file(self, start_time: TimeStamp):
        command = [
            "vlc",
            f'"{self.filename}"'.replace("/", "\\"),
            "--start-time",
            str(int(start_time.seconds_value())),
        ]

        command = " ".join(command)

        for sound_player_window in pygetwindow.getWindowsWithTitle("VLC media player"):
            sound_player_window.close()
        await self.wait_for_window("VLC media player", self.is_window_closed)

        await asyncio.create_subprocess_shell(command)

        window_open = await self.wait_for_window(
            "VLC media player", self.is_window_open
        )
        if not window_open:
            raise TimeoutError("Potplayer takes too long to open")

        # print(f"Window for '{command}' is open.")
        # adjust window
        sound_player_window = pygetwindow.getWindowsWithTitle("VLC media player")[0]
        x_offset = -15
        x_size_offset = 17
        sound_player_window.moveTo(
            int(SCREEN_WIDTH * 0.7) + x_offset, int(SCREEN_HEIGHT * 0.7)
        )
        sound_player_window.resizeTo(
            int(SCREEN_WIDTH * 0.3) + x_size_offset, int(SCREEN_HEIGHT * 0.3)
        )

    def convert(self, text):
        text = self._check_text(text)
        audio_content = self._make_request(text)
        if audio_content:
            with wave.open(self.filename, "wb") as file:
                sample_width = 1  # 8-bit audio, 1 byte per sample
                sample_rate = 8000  # 8 kHz sample rate
                num_channels = 1
                file.setsampwidth(sample_width)
                file.setframerate(sample_rate)
                file.setnchannels(num_channels)
                file.writeframes(audio_content)

    def _check_text(self, text):
        text = text.encode("utf-8").decode("utf-8")
        text = text.replace("\n", " ")

        # # print(f"Size of text: {sys.getsizeof(text)}")
        if sys.getsizeof(text) > 98_000:
            raise MemoryError("Text size exceeds the maximum allowed size")
        return text

    def _make_request(self, text):
        self.url = "https://api.voicerss.org/"
        with open("../../VoiceRSS.txt") as file:
            self.key_code = next(file).strip()
        self.hl = "en-us"
        self.voice = "Mary"
        params = {"key": self.key_code, "src": text, "hl": self.hl, "v": self.voice}
        response = requests.post(self.url, data=params)
        response.raise_for_status()
        if response.status_code == 200:
            audio_content = response.content
            return audio_content
