import time


def run_walk_timer(duration_minutes: int):
    total_seconds = duration_minutes * 60

    for remaining in range(total_seconds, 0, -1):
        yield {
            "remaining_seconds": remaining,
            "total_seconds": total_seconds,
        }
        time.sleep(1)
