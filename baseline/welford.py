import math


def update(count: int, mean: float, m2: float, new_value: float) -> tuple[int, float, float]:
    count += 1
    delta = new_value - mean
    mean += delta / count
    delta2 = new_value - mean
    m2 += delta * delta2
    return count, mean, m2


def finalize(count: int, mean: float, m2: float) -> tuple[float, float | None]:
    if count < 2:
        return mean, None

    variance = m2 / (count - 1)
    return mean, math.sqrt(variance)
