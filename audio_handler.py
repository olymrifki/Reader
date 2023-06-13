import subprocess
import sys
import time
import wave
from datetime import timedelta

import pygetwindow as gw
import requests


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

    def open_file_with_potplayer(self, start_time: TimeStamp):
        subprocess.Popen(
            [
                "PotPlayerMini",
                self.filename,
                "/new",
                f"/seek={str(start_time)}",
            ]
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

        # print(f"Size of text: {sys.getsizeof(text)}")
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
            print("Audio recieved")
            audio_content = response.content
            return audio_content


if __name__ == "__main__":
    tts = AudioHandler()
    filename = "./extracted_text.txt"
    with open(filename, "r", encoding="utf-8") as file:
        text_data = file.read()
    tts.convert(text_data)

    # output_file = "extracted_text.txt"
    # with open(output_file, "w", encoding="utf-8") as file:
    #     file.write(text)

    # time.sleep(2)
    # with open(output_file, "r", encoding="utf-8") as file:
    #     text = file.read()

    # if __name__ == "__main__":
    filename = "./audio_file.wav"
    popener = AudioHandler(filename)

    popener.open_file_with_potplayer()
    # Get the primary screen
    # screen = gw.getScreenInfo()[0]
    time.sleep(2)
    # Get the screen size
    screen_width = 1280
    screen_height = 720
    # print(len(gw.getWindowsWithTitle("PotPlayer")))
    potplayer_window = gw.getWindowsWithTitle("PotPlayer")[0]
    # potplayer_window.waitForWindow()
    potplayer_window.resizeTo(int(screen_width * 0.8), int(screen_height * 0.25))

    potplayer_window.moveTo(-300, 200)
