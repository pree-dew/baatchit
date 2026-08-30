import asyncio

import sounddevice as sd
import soundfile as sf


def play_audio(path: str) -> None:
    audio, sr = sf.read(path)
    sd.play(audio, sr)
    sd.wait()


async def play_audio_interruptible(path: str, stop_check) -> bool:
    audio, sr = sf.read(path)
    sd.play(audio, sr)

    stream = sd.get_stream()
    while stream.active:
        if stop_check():
            sd.stop()
            return True
        await asyncio.sleep(0.1)

    return False
