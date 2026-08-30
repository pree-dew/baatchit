from baseline.store import get_zscore

FEATURE_WEIGHTS = {
    "pitch_std": 1.0,
    "rms_energy": 1.0,
    "speaking_rate": 0.8,
    "pause_ratio": 0.6,
    "pitch_mean": 0.5,
    "jitter": 0.2,
    "shimmer": 0.2,
}


def compute_activation(features: dict) -> float | None:
    weighted_sum = 0.0
    total_weight = 0.0

    for feature_name, weight in FEATURE_WEIGHTS.items():
        value = features.get(feature_name)
        if value is None:
            continue

        z = get_zscore(feature_name, value)
        if z is None:
            continue

        weighted_sum += abs(z) * weight
        total_weight += weight

    if total_weight == 0:
        return None

    return weighted_sum / total_weight
