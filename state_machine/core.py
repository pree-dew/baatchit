import datetime
import json

from baseline.describe import describe_prosody
from db import db as db_module
from llm.agent import get_response
from llm.reflect import generate_notes
from scoring import ema as scoring_ema
from state_machine import improvement_detector
from state_machine.states import Stage

INTERVENTION_ACTIONS = {"breathing", "walk_timer", "music", "distraction", "journal", "soothing_images"}


class SessionCore:
    def __init__(self) -> None:
        self.session_id = db_module.insert_session(started_at=datetime.datetime.now().isoformat())
        self.stage = Stage.VENTING
        self.conversation_history: list[dict] = []
        self.turn_index = 0

        self.last_intervention_id: int | None = None
        self.last_intervention_type: str | None = None
        self.last_intervention_emotion: str | None = None
        self.closing_followup_used = False
        self.pending_preference_text: str | None = None

    def handle_turn(self, transcript: str, features: dict) -> dict:
        if self.stage == Stage.CLOSING and self.closing_followup_used:
            self.pending_preference_text = transcript

        prosody_context = describe_prosody(features)
        personality_notes = db_module.get_personality_notes()
        intervention_scores = scoring_ema.get_all_scores()

        forced_tool = "close_session" if (self.stage == Stage.CLOSING and self.closing_followup_used) else None

        response = get_response(
            transcript=transcript,
            conversation_history=self.conversation_history,
            stage=self.stage,
            personality_notes=personality_notes,
            prosody_context=prosody_context,
            intervention_scores=intervention_scores,
            forced_tool=forced_tool,
        )

        self.conversation_history.append({"role": "user", "content": transcript})
        self.conversation_history.append({"role": "assistant", "content": response["spoken_text"]})

        db_module.insert_utterance(
            session_id=self.session_id,
            turn_index=self.turn_index,
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
        self.turn_index += 1

        action = response["action"]
        result = {"action": action, "spoken_text": response["spoken_text"], "closed": False}

        if action == "close_session":
            result["closed"] = True
            result["outcome"] = response["outcome"]
            self._resolve_session(response["outcome"])
            return result

        if action == "check_in":
            self.stage = Stage.CLOSING

        elif action in INTERVENTION_ACTIONS:
            result["intervention_args"] = {
                k: v for k, v in response.items() if k not in ("action", "spoken_text")
            }

        elif self.stage == Stage.MONITORING:
            if improvement_detector.should_check_in(features):
                self.stage = Stage.CHECKING_IN

        elif self.stage == Stage.CLOSING and action == "just_listen":
            self.closing_followup_used = True

        return result

    def record_intervention_result(self, action: str, args: dict, spoken_text: str, stopped_early: bool) -> int:
        action_params = dict(args)
        action_params["stopped_early"] = stopped_early
        intervention_id = db_module.insert_intervention(
            session_id=self.session_id,
            action=action,
            action_params=json.dumps(action_params),
            spoken_text=spoken_text,
            started_at=datetime.datetime.now().isoformat(),
        )
        self.last_intervention_id = intervention_id
        self.last_intervention_type = action
        self.last_intervention_emotion = args.get("emotion")

        is_first_intervention = self.stage != Stage.MONITORING
        self.stage = Stage.MONITORING
        improvement_detector.start_monitoring_window(is_first_intervention)

        return intervention_id

    def _resolve_session(self, outcome: str) -> list[dict]:
        if self.last_intervention_id is not None:
            db_module.insert_feedback(
                intervention_id=self.last_intervention_id,
                outcome=outcome,
                recorded_at=datetime.datetime.now().isoformat(),
                user_preference_text=self.pending_preference_text,
            )
            scoring_ema.update_score(
                intervention_type=self.last_intervention_type,
                emotion=self.last_intervention_emotion,
                outcome=1.0 if outcome == "helped" else 0.0,
            )

        conversation_summary = "\n".join(
            f"{m['role']}: {m['content']}" for m in self.conversation_history
        )
        notes = generate_notes(conversation_summary, outcome)
        for note in notes:
            db_module.insert_personality_note(
                category=note["category"],
                note_text=note["note_text"],
                created_at=datetime.datetime.now().isoformat(),
            )
        return notes
