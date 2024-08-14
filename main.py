import threading
from audio import record_system_audio
from screen import record_screen, capture_screen
from gui import ScreenRecorderApp, notify_send
import subprocess
import argparse
from datetime import datetime
from config import FOLDER
import os
import queue
import cv2

result_queue = queue.Queue()


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


def turn_video_to_gif(video_file, output_file):
    # 使用 ffmpeg 将音频和视频合成一个 mp4 文件
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        "fps=10",
        output_file,
    ]
    print("running command:")
    print(" ".join(command))
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Audio and video merged into {output_file}")


def save_video():
    mp4_name = get_file_path("mp4")
    # 合并音频和视频
    print("merging audio and video...")
    notify_send("merging audio and video...")
    merge_audio_video("/tmp/_output.mp4", "/tmp/_output.wav", mp4_name)
    print(f"Video saved to {mp4_name}")
    notify_send(f"Video saved to {mp4_name}")


def save_gif():
    gif_name = get_file_path("gif")
    print("Creating gif...")
    notify_send("Creating gif...")
    turn_video_to_gif("/tmp/_output.mp4", gif_name)
    print(f"Gif saved to {gif_name}")
    notify_send(f"Gif saved to {gif_name}")


def exec_capture(app):
    def _exec_capture():
        def wrapper():
            frame = capture_screen(app.bbox)
            result_queue.put(frame)

        capture_thread = threading.Thread(target=wrapper)

        capture_thread.start()
        capture_thread.join()

        captured_frame = result_queue.get()
        # save the captured frame
        filename = get_file_path("png")
        cv2.imwrite(filename, captured_frame)
        notify_send(f"Image saved to {filename}")

    return _exec_capture


def start_video(app):
    def _start_video():
        stop_event = threading.Event()
        audio_thread = threading.Thread(
            target=record_system_audio, args=(stop_event,)
        )
        video_thread = threading.Thread(
            target=record_screen,
            args=(
                app.bbox,
                stop_event,
            ),
        )

        video_thread.start()
        audio_thread.start()

        return stop_event, video_thread, audio_thread

    return _start_video


def start_gif(app):
    def _start_gif():
        stop_event = threading.Event()
        video_thread = threading.Thread(
            target=record_screen,
            args=(
                app.bbox,
                stop_event,
            ),
        )

        video_thread.start()

        return stop_event, video_thread

    return _start_gif


def main():
    print("Select screen area to record...")

    app = ScreenRecorderApp()

    app.register_capture_image_hook(exec_capture(app))
    app.register_video_hooks(start_video(app), save_video)
    app.register_gif_hooks(start_gif(app), save_gif)

    app.run()


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
