import librosa
import numpy as np


def extract_intensity(y: np.ndarray, sr: int) -> float:
    rms = librosa.feature.rms(y=y)[0]
    return float(np.mean(rms))
