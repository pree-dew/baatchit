import tempfile
from pathlib import Path
from typing import AsyncIterator

from openai import AsyncOpenAI, OpenAI

import config
from audio.player import play_audio

_client = OpenAI(api_key=config.OPENAI_API_KEY)
_async_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

MODEL = "tts-1"
VOICE = "onyx"


def synthesize(text: str) -> bytes:
    response = _client.audio.speech.create(
        model=MODEL,
        voice=VOICE,
        input=text,
        response_format="wav",
    )
    return response.read()


async def stream_speech(text: str) -> AsyncIterator[bytes]:
    # mp3 has no upfront total-length header (unlike wav), so a browser can
    # play frames as they arrive instead of waiting for the whole file.
    async with _async_client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice=VOICE,
        input=text,
        response_format="mp3",
    ) as response:
        async for chunk in response.iter_bytes(4096):
            yield chunk


def speak(text: str) -> None:
    audio_bytes = synthesize(text)

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = Path(tmp_dir) / "speech.wav"
        out_path.write_bytes(audio_bytes)
        play_audio(str(out_path))
