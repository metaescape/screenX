import wave
import sys

import pyaudio


def record_microphone():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 if sys.platform == "darwin" else 2
    RATE = 44100
    RECORD_SECONDS = 5

    with wave.open("output.wav", "wb") as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, input=True
        )

        print("Recording...")
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
        print("Done")

        stream.close()
        p.terminate()


def record_system_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 if sys.platform == "darwin" else 2
    RATE = 44100
    RECORD_SECONDS = 10

    with wave.open("output.wav", "wb") as wf:
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(info)
            if "pulse" in info["name"]:
                device_index = i
                print(
                    f"Found PulseAudio virtual device at index {device_index}"
                )
                break

        if device_index is None:
            print("PulseAudio virtual device not found")
            return
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
        )

        print("Recording...")
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
        print("Done")

        stream.close()
        p.terminate()


if __name__ == "__main__":
    record_system_audio()
