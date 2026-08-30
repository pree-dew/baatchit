from openai import OpenAI

import config

_client = OpenAI(api_key=config.OPENAI_API_KEY)


def transcribe(path: str) -> dict:
    with open(path, "rb") as audio_file:
        response = _client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )

    return {
        "text": response.text,
        "words": [
            {"word": w.word, "start": w.start, "end": w.end}
            for w in response.words
        ],
    }
