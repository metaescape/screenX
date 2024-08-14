import threading
from audio import record_system_audio
from screen import record_screen, capture_screen
from gui import ScreenRecorderApp
from functools import partial
import subprocess
import argparse
from datetime import datetime
from config import FOLDER
import os


def get_file_path(ext="mp4"):
    # using datetime as file name
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    return f"{os.path.expanduser(FOLDER)}/{filename}.{ext}"


def merge_audio_video(video_file, audio_file, output_file):
    # 使用 ffmpeg 将音频和视频合成一个 mp4 文件
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-i",
        audio_file,
        "-vcodec",
        "libx264",
        "-acodec",
        "libmp3lame",
        "-y",
        output_file,
    ]
    print("running command:")
    print(" ".join(command))
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Audio and video merged into {output_file}")


def notify_send(message, seconds=5):
    # 使用 notify-send 发送通知
    command = ["notify-send", message, "-t", str(seconds * 1000)]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():

    print("Select screen area to record...")

    stop_event = threading.Event()

    app = ScreenRecorderApp()

    capture_thread = threading.Thread(
        target=partial(capture_screen),
        args=(app.bbox, lambda: get_file_path("png")),
    )

    def exec_capture():
        capture_thread.start()
        notify_send(f"png file saved to {get_file_path('png')} ")
        exit(0)

    app.register_capture_image_hook(exec_capture)

    audio_thread = threading.Thread(
        target=record_system_audio, args=(stop_event,)
    )
    video_thread = threading.Thread(
        target=partial(record_screen, app.bbox), args=(stop_event,)
    )

    def start_thread():

        video_thread.start()
        audio_thread.start()

    app.register_recording_hook(start_thread)

    def stop_thread():
        stop_event.set()

        audio_thread.join()
        video_thread.join()

    app.register_end_hook(stop_thread)

    mp4_name = get_file_path("mp4")

    app.run()

    # 合并音频和视频
    print("merging audio and video...")
    notify_send("merging audio and video...")
    merge_audio_video("/tmp/_output.mp4", "/tmp/_output.wav", mp4_name)
    print(f"Video saved to {mp4_name}")
    notify_send(f"Video saved to {mp4_name}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # arg parser for main and merge_audio_video
    parser.add_argument(
        "--full", "-f", action="store_true", help="Run the main function"
    )

    args = parser.parse_args()
    if args.full:
        main()
    else:
        merge_audio_video(
            "/tmp/_output.mp4", "/tmp/_output.wav", "/tmp/output.mp4"
        )
