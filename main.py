import threading
from audio import record_system_audio
from screen import record_screen
from gui import ScreenRecorderApp
from functools import partial
import subprocess
import argparse


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


def main():

    print("Select screen area to record...")

    stop_event = threading.Event()

    app = ScreenRecorderApp()
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

    app.run()

    # 合并音频和视频
    print("merging audio and video...")
    merge_audio_video("_output.mp4", "_output.wav", "output.mp4")
    print("output.mp4 created.")


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
        merge_audio_video("_output.mp4", "_output.wav", "output.mp4")
