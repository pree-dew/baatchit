import librosa

import config
from prosody.intensity import extract_intensity
from prosody.jitter_shimmer import extract_jitter_shimmer
from prosody.pauses import extract_pause_ratio
from prosody.pitch import extract_pitch
from prosody.rate import extract_speaking_rate


def extract_features(path: str, words: list[dict]) -> dict:
    y, sr = librosa.load(path, sr=config.SAMPLE_RATE, mono=True)

    pitch_mean, pitch_std = extract_pitch(y, sr)
    rms_energy = extract_intensity(y, sr)
    jitter, shimmer = extract_jitter_shimmer(y, sr)
    speaking_rate = extract_speaking_rate(words)
    pause_ratio = extract_pause_ratio(words)

    return {
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "rms_energy": rms_energy,
        "jitter": jitter,
        "shimmer": shimmer,
        "speaking_rate": speaking_rate,
        "pause_ratio": pause_ratio,
    }
