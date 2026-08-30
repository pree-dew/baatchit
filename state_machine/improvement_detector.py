import time

import config
from baseline.activation import compute_activation

peak_activation: float | None = None
first_intervention_started_at: float | None = None
turns_since_first_intervention: int = 0


def start_monitoring_window(is_first_intervention: bool) -> None:
    global peak_activation, first_intervention_started_at, turns_since_first_intervention
    peak_activation = None
    if is_first_intervention:
        first_intervention_started_at = time.time()
        turns_since_first_intervention = 0


def should_check_in(features: dict) -> bool:
    global peak_activation, turns_since_first_intervention

    turns_since_first_intervention += 1
    activation = compute_activation(features)

    if activation is not None:
        if peak_activation is None or activation > peak_activation:
            peak_activation = activation
        elif peak_activation > 0:
            drop = (peak_activation - activation) / peak_activation
            if drop >= config.AROUSAL_DROP_THRESHOLD:
                return True

    elapsed = time.time() - first_intervention_started_at
    if (
        turns_since_first_intervention >= config.CHECK_IN_TIMEOUT_TURNS
        or elapsed >= config.CHECK_IN_TIMEOUT_SECONDS
    ):
        return True

    return False
