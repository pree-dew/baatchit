import tempfile
from pathlib import Path

from openai import OpenAI

import config
from audio.player import play_audio

_client = OpenAI(api_key=config.OPENAI_API_KEY)

MODEL = "tts-1"
VOICE = "onyx"


def speak(text: str) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = Path(tmp_dir) / "speech.wav"

        response = _client.audio.speech.create(
            model=MODEL,
            voice=VOICE,
            input=text,
            response_format="wav",
        )
        response.write_to_file(out_path)

        play_audio(str(out_path))
