import sys
import time
import wave

import requests
from requests.exceptions import HTTPError


class Text2Speech:
    def __init__(self) -> None:
        # self.savedir = directory
        self.url = "https://api.voicerss.org/"
        with open("../../VoiceRSS.txt") as file:
            self.key_code = next(file).strip()
        self.hl = "en-us"
        self.v = "Mary"

    def check_text(self, text):
        text = text.encode("utf-8").decode("utf-8")
        text = text.replace("\n", " ")

        # print(f"Size of text: {sys.getsizeof(text)}")
        if sys.getsizeof(text) > 98_000:
            raise MemoryError("Text size exceeds the maximum allowed size")
        return text

    def make_request(self, text):
        params = {"key": self.key_code, "src": text, "hl": self.hl, "v": self.v}
        response = requests.post(self.url, data=params)
        response.raise_for_status()
        if response.status_code == 200:
            print("Audio recieved")
            audio_content = response.content
            return audio_content

    def convert(self, text, filename="audio_file.wav"):
        text = self.check_text(text)
        audio_content = self.make_request(text)
        if audio_content:
            with wave.open(filename, "wb") as file:
                sample_width = 1  # 8-bit audio, 1 byte per sample
                sample_rate = 8000  # 8 kHz sample rate
                num_channels = 1
                file.setsampwidth(sample_width)
                file.setframerate(sample_rate)
                file.setnchannels(num_channels)
                file.writeframes(audio_content)

            # time.sleep(10)


if __name__ == "__main__":
    tts = Text2Speech()
    file_path = "./extracted_text.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        text_data = file.read()
    tts.convert(text_data)

    # output_file = "extracted_text.txt"
    # with open(output_file, "w", encoding="utf-8") as file:
    #     file.write(text)

    # time.sleep(2)
    # with open(output_file, "r", encoding="utf-8") as file:
    #     text = file.read()
