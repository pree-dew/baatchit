import sys


async def render_breathing(state_stream, stop_check) -> bool:
    last_cycle = None

    async for state in state_stream:
        if stop_check():
            print("\nStopped.")
            return True

        if state["cycle"] != last_cycle:
            print(f"\n-- cycle {state['cycle']} of {state['total_cycles']} --")
            last_cycle = state["cycle"]

        sys.stdout.write(f"\r{state['phase']}... {state['seconds_remaining']}  ")
        sys.stdout.flush()

    sys.stdout.write("\rDone.                    \n")
    sys.stdout.flush()
    return False


async def render_walk_timer(state_stream, stop_check) -> bool:
    async for state in state_stream:
        if stop_check():
            print("\nStopped.")
            return True

        minutes = state["remaining_seconds"] // 60
        seconds = state["remaining_seconds"] % 60
        sys.stdout.write(f"\rWalk timer... {minutes}:{seconds:02d}  ")
        sys.stdout.flush()

    sys.stdout.write("\rWalk complete.                    \n")
    sys.stdout.flush()
    return False
