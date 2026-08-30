from baseline.store import get_zscore

FEATURES_TO_DESCRIBE = ["pitch_mean", "pitch_std", "rms_energy", "speaking_rate", "pause_ratio"]
ZSCORE_THRESHOLD = 1.0


def describe_prosody(features: dict) -> str:
    descriptions = []

    for name in FEATURES_TO_DESCRIBE:
        value = features.get(name)
        if value is None:
            continue

        z = get_zscore(name, value)
        if z is None or abs(z) <= ZSCORE_THRESHOLD:
            continue

        direction = "higher" if z > 0 else "lower"
        readable_name = name.replace("_", " ")
        descriptions.append(f"{readable_name} notably {direction} than usual")

    return "; ".join(descriptions)
