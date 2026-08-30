import asyncio

from audio.recorder import record_until_silence
from interventions.breathing import run_breathing
from interventions.distraction import run_distraction
from interventions.interrupt import stop_requested
from interventions.journal import run_journal
from interventions.music import play_music
from interventions.soothing_images import show_soothing_image
from interventions.terminal_render import render_breathing, render_walk_timer
from interventions.walk_timer import run_walk_timer
from prosody.features import extract_features
from state_machine.core import SessionCore
from stt.transcribe import transcribe
from tts.speak import speak

RECORDING_PATH = "data/recordings/_turn.wav"

INTERVENTION_DISPATCH = {
    "breathing": lambda args: render_breathing(run_breathing(args["pace"]), stop_requested),
    "walk_timer": lambda args: render_walk_timer(run_walk_timer(args["duration_minutes"]), stop_requested),
    "music": lambda args: play_music(args["mood"], stop_requested),
    "distraction": lambda args: run_distraction(args["style"], stop_requested),
    "journal": lambda args: run_journal(args["prompt_theme"], stop_requested),
    "soothing_images": lambda args: show_soothing_image(args["theme"], stop_requested),
}


async def run_session() -> None:
    core = SessionCore()

    while True:
        print("\nListening...")
        path = record_until_silence(RECORDING_PATH)

        result = transcribe(path)
        transcript, words = result["text"], result["words"]
        print(f"You said: {transcript}")

        features = extract_features(path, words)

        turn_result = core.handle_turn(transcript, features)

        speak(turn_result["spoken_text"])

        if turn_result["closed"]:
            print("\n[session closed]")
            return

        action = turn_result["action"]

        if action in INTERVENTION_DISPATCH:
            args = turn_result["intervention_args"]
            stopped_early = await INTERVENTION_DISPATCH[action](args)
            core.record_intervention_result(action, args, turn_result["spoken_text"], stopped_early)
            print(f"\n[intervention logged, stopped_early={stopped_early}] moving to monitoring")


if __name__ == "__main__":
    asyncio.run(run_session())
