import subprocess
import time

import pygetwindow as gw

# import time


class AudioOpener:
    def __init__(self, file_path) -> None:
        if file_path.endswith(".wav") or file_path.endswith(".mp3"):
            self.file_path = file_path
        else:
            raise ValueError("Wrong file type.")

    def open_file_with_potplayer(self, start_time="00:00:00"):
        subprocess.Popen(
            [
                "PotPlayerMini",
                self.file_path,
                "/new",
                f"/seek={start_time}",
            ]
        )


if __name__ == "__main__":
    file_path = "./audio_file.wav"
    popener = AudioOpener(file_path)

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
