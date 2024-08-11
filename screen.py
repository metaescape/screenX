"""
functions for screen recording
"""

import cv2
import numpy as np
import mss
from time import time, sleep
import threading


def record_screen(bbox, stop_event):
    fps = 25
    frame_time = 1.0 / fps
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    video = cv2.VideoWriter(
        "_output.mp4", fourcc, fps, (bbox["width"], bbox["height"])
    )

    with mss.mss() as sct:
        last_frame_time = time()
        print("Recording screen...")
        while not stop_event.is_set():
            current_time = time()
            elapsed_time = current_time - last_frame_time

            if elapsed_time < frame_time:
                sleep(frame_time - elapsed_time)
                continue

            last_frame_time = time()

            sct_img = sct.grab(bbox)
            frame = np.array(sct_img)

            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

            video.write(frame)

    video.release()
    cv2.destroyAllWindows()
    print("Screen recording stopped.")


def test_recording():
    # 创建一个停止事件
    stop_event = threading.Event()

    # 启动录制线程
    video_thread = threading.Thread(target=record_screen, args=(stop_event,))
    video_thread.start()

    # 模拟录制一段时间
    sleep(5)  # 录制5秒

    # 停止录制
    print("Stopping recording...")
    stop_event.set()

    # 等待录制线程结束
    video_thread.join()
    print("Recording stopped and saved to '_output.mp4'")


if __name__ == "__main__":
    test_recording()
