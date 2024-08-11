import cv2
import numpy as np
import mss
from time import time
import pyaudio


AUDIO_RATE = 44100
AUDIO_CHANNELS = 2
CHUNK = 1024


def audio_stream(queue):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=AUDIO_CHANNELS,
        rate=AUDIO_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    while True:
        data = stream.read(CHUNK)
        queue.put(data)


def main():
    bbox = {"top": 0, "left": 0, "width": 128, "height": 128}
    fps = 25
    frame_delta = 1 / fps
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    video = cv2.VideoWriter(
        "output.mp4", fourcc, fps, (bbox["width"], bbox["height"])
    )

    with mss.mss() as sct:
        next_frame = time()
        while True:
            next_frame += frame_delta
            sct_img = sct.grab(bbox)
            frame = np.array(sct_img)

            if frame is None:
                continue

            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

            video.write(frame)

            cv2.imshow("Screen Capture", frame)

            # calculate wait time to meet the defined fps
            wait_ms = max(int((next_frame - time()) * 1000), 1)

            if cv2.waitKey(wait_ms) & 0xFF == 27:
                break

    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
