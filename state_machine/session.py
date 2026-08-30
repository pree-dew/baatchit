import datetime
import json

from audio.recorder import record_until_silence
from baseline.describe import describe_prosody
from db import db as db_module
from interventions.breathing import run_breathing
from interventions.distraction import run_distraction
from interventions.interrupt import stop_requested
from interventions.journal import run_journal
from interventions.music import play_music
from interventions.soothing_images import show_soothing_image
from interventions.terminal_render import render_breathing, render_walk_timer
from interventions.walk_timer import run_walk_timer
from llm.agent import get_response
from llm.reflect import generate_notes
from prosody.features import extract_features
from scoring import ema as scoring_ema
from state_machine import improvement_detector
from state_machine.states import Stage
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


def run_session() -> None:
    session_id = db_module.insert_session(started_at=datetime.datetime.now().isoformat())
    stage = Stage.VENTING
    conversation_history: list[dict] = []
    turn_index = 0

    last_intervention_id: int | None = None
    last_intervention_type: str | None = None
    last_intervention_emotion: str | None = None
    closing_followup_used = False
    pending_preference_text: str | None = None

    while True:
        print("\nListening...")
        path = record_until_silence(RECORDING_PATH)

        result = transcribe(path)
        transcript, words = result["text"], result["words"]
        print(f"You said: {transcript}")

        if stage == Stage.CLOSING and closing_followup_used:
            pending_preference_text = transcript

        features = extract_features(path, words)
        prosody_context = describe_prosody(features)
        personality_notes = db_module.get_personality_notes()
        intervention_scores = scoring_ema.get_all_scores()

        forced_tool = "close_session" if (stage == Stage.CLOSING and closing_followup_used) else None

        response = get_response(
            transcript=transcript,
            conversation_history=conversation_history,
            stage=stage,
            personality_notes=personality_notes,
            prosody_context=prosody_context,
            intervention_scores=intervention_scores,
            forced_tool=forced_tool,
        )

        conversation_history.append({"role": "user", "content": transcript})
        conversation_history.append({"role": "assistant", "content": response["spoken_text"]})

        db_module.insert_utterance(
            session_id=session_id,
            turn_index=turn_index,
            transcript=transcript,
            pitch_mean=features["pitch_mean"],
            pitch_std=features["pitch_std"],
            rms_energy=features["rms_energy"],
            jitter=features["jitter"],
            shimmer=features["shimmer"],
            speaking_rate=features["speaking_rate"],
            pause_ratio=features["pause_ratio"],
            timestamp=datetime.datetime.now().isoformat(),
        )
        turn_index += 1

        speak(response["spoken_text"])

        action = response["action"]

        if action == "close_session":
            outcome = response["outcome"]
            if last_intervention_id is not None:
                db_module.insert_feedback(
                    intervention_id=last_intervention_id,
                    outcome=outcome,
                    recorded_at=datetime.datetime.now().isoformat(),
                    user_preference_text=pending_preference_text,
                )
                scoring_ema.update_score(
                    intervention_type=last_intervention_type,
                    emotion=last_intervention_emotion,
                    outcome=1.0 if outcome == "helped" else 0.0,
                )

            conversation_summary = "\n".join(
                f"{m['role']}: {m['content']}" for m in conversation_history
            )
            notes = generate_notes(conversation_summary, outcome)
            for note in notes:
                db_module.insert_personality_note(
                    category=note["category"],
                    note_text=note["note_text"],
                    created_at=datetime.datetime.now().isoformat(),
                )
            print(f"\n[session closed, {len(notes)} new personality note(s) saved]")
            return

        if action == "check_in":
            stage = Stage.CLOSING

        elif action in INTERVENTION_DISPATCH:
            stopped_early = INTERVENTION_DISPATCH[action](response)

            action_params = {k: v for k, v in response.items() if k not in ("action", "spoken_text")}
            action_params["stopped_early"] = stopped_early
            intervention_id = db_module.insert_intervention(
                session_id=session_id,
                action=action,
                action_params=json.dumps(action_params),
                spoken_text=response["spoken_text"],
                started_at=datetime.datetime.now().isoformat(),
            )
            last_intervention_id = intervention_id
            last_intervention_type = action
            last_intervention_emotion = response.get("emotion")

            print(f"\n[intervention logged, id={intervention_id}, stopped_early={stopped_early}] moving to monitoring")
            is_first_intervention = stage != Stage.MONITORING
            stage = Stage.MONITORING
            improvement_detector.start_monitoring_window(is_first_intervention)

        elif stage == Stage.MONITORING:
            if improvement_detector.should_check_in(features):
                print("\n[improvement detector fired] moving to checking_in")
                stage = Stage.CHECKING_IN

        elif stage == Stage.CLOSING and action == "just_listen":
            closing_followup_used = True


if __name__ == "__main__":
    run_session()
