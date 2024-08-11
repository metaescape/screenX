import wave
import sys
import threading
from time import sleep
import pyaudio


def get_system_audio_devices(p: pyaudio.PyAudio):
    device_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if "pulse" in info["name"]:
            device_index = i
            print(f"Found PulseAudio virtual device at index {device_index}")
            break

    if device_index is None:
        raise ValueError("PulseAudio virtual device not found")


def record_system_audio(stop_event):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 if sys.platform == "darwin" else 2
    RATE = 44100

    p = pyaudio.PyAudio()
    device_index = get_system_audio_devices(p)

    with wave.open("_output.wav", "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK,
        )

        print("Recording system audio...")
        while not stop_event.is_set():
            wf.writeframes(stream.read(CHUNK))
        print("Audio recording stopped.")

    stream.stop_stream()
    stream.close()
    p.terminate()


def test_recording():
    # 创建一个停止事件
    stop_event = threading.Event()

    # 启动录制线程
    video_thread = threading.Thread(
        target=record_system_audio, args=(stop_event,)
    )
    video_thread.start()

    # 模拟录制一段时间
    sleep(5)  # 录制5秒

    # 停止录制
    print("Stopping recording...")
    stop_event.set()

    # 等待录制线程结束
    video_thread.join()
    print("Recording stopped and saved to '_output.wav'")


if __name__ == "__main__":
    test_recording()
