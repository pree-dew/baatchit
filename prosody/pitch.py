import librosa
import numpy as np

FMIN = librosa.note_to_hz("C2")
FMAX = librosa.note_to_hz("C7")


def extract_pitch(y: np.ndarray, sr: int) -> tuple[float | None, float | None]:
    f0, voiced_flag, _ = librosa.pyin(y, fmin=FMIN, fmax=FMAX, sr=sr)
    voiced_f0 = f0[voiced_flag]

    if voiced_f0.size == 0:
        return None, None

    return float(np.nanmean(voiced_f0)), float(np.nanstd(voiced_f0))
