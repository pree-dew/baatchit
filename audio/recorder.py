from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import torch
from silero_vad import load_silero_vad

import config

CHUNK_SIZE = 512  # samples per chunk; required by Silero at 16kHz
SPEECH_PROB_THRESHOLD = 0.5
BASE_HANGOVER_SECONDS = 3.0
GROWTH_STEP_SECONDS = 0.8
MAX_HANGOVER_SECONDS = 6.0
DECAY_RATE = 0.7
MAX_DURATION_SECONDS = 300.0

_model = load_silero_vad()


def record_until_silence(out_path: str) -> str:
    chunk_duration = CHUNK_SIZE / config.SAMPLE_RATE
    max_chunks = int(MAX_DURATION_SECONDS / chunk_duration)

    chunks = []
    consecutive_silent_chunks = 0
    current_hangover_seconds = BASE_HANGOVER_SECONDS

    with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1, dtype="float32") as stream:
        for _ in range(max_chunks):
            chunk, _ = stream.read(CHUNK_SIZE)
            chunks.append(chunk.copy())

            chunk_tensor = torch.from_numpy(chunk.flatten())
            speech_prob = _model(chunk_tensor, config.SAMPLE_RATE).item()
            is_speech = speech_prob >= SPEECH_PROB_THRESHOLD

            if is_speech:
                if consecutive_silent_chunks > 0:
                    current_hangover_seconds = min(
                        current_hangover_seconds + GROWTH_STEP_SECONDS,
                        MAX_HANGOVER_SECONDS,
                    )
                consecutive_silent_chunks = 0
            else:
                consecutive_silent_chunks += 1
                silence_duration = consecutive_silent_chunks * chunk_duration
                effective_threshold = max(
                    BASE_HANGOVER_SECONDS,
                    current_hangover_seconds - DECAY_RATE * silence_duration,
                )
                if silence_duration >= effective_threshold:
                    break

    audio = np.concatenate(chunks, axis=0)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_path, audio, config.SAMPLE_RATE)
    return out_path
