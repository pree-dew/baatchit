def extract_pause_ratio(words: list[dict]) -> float | None:
    if len(words) < 2:
        return None

    speaking_duration = words[-1]["end"] - words[0]["start"]
    if speaking_duration <= 0:
        return None

    total_pause_time = sum(
        max(0.0, words[i + 1]["start"] - words[i]["end"])
        for i in range(len(words) - 1)
    )

    return total_pause_time / speaking_duration
