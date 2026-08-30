import time

PACE_PATTERNS = {
    "4-7-8": [("Breathe in", 4), ("Hold", 7), ("Breathe out", 8)],
    "box": [("Breathe in", 4), ("Hold", 4), ("Breathe out", 4), ("Hold", 4)],
    "simple_slow": [("Breathe in", 4), ("Breathe out", 6)],
}

CYCLES = 3


def run_breathing(pace: str):
    pattern = PACE_PATTERNS[pace]

    for cycle in range(1, CYCLES + 1):
        for phase, seconds in pattern:
            for remaining in range(seconds, 0, -1):
                yield {
                    "phase": phase,
                    "seconds_remaining": remaining,
                    "cycle": cycle,
                    "total_cycles": CYCLES,
                }
                time.sleep(1)
