import numpy as np
import parselmouth
from parselmouth.praat import call

FMIN = 75
FMAX = 500


def extract_jitter_shimmer(y: np.ndarray, sr: int) -> tuple[float | None, float | None]:
    sound = parselmouth.Sound(y.astype(np.float64), sampling_frequency=sr)
    point_process = call(sound, "To PointProcess (periodic, cc)", FMIN, FMAX)

    if call(point_process, "Get number of points") < 2:
        return None, None

    jitter = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
    shimmer = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)

    jitter = None if np.isnan(jitter) else float(jitter)
    shimmer = None if np.isnan(shimmer) else float(shimmer)

    return jitter, shimmer
