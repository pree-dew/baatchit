def extract_speaking_rate(words: list[dict]) -> float | None:
    if not words:
        return None

    speaking_duration = words[-1]["end"] - words[0]["start"]
    if speaking_duration <= 0:
        return None

    return len(words) / speaking_duration
