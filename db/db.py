import sqlite3
from pathlib import Path

import config

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema_sql = SCHEMA_PATH.read_text()
    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def insert_session(started_at: str) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO sessions (started_at) VALUES (?)",
            (started_at,),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def insert_utterance(
    session_id: int,
    turn_index: int,
    transcript: str,
    pitch_mean: float,
    pitch_std: float,
    rms_energy: float,
    jitter: float,
    shimmer: float,
    speaking_rate: float,
    pause_ratio: float,
    timestamp: str,
) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO utterances (
                session_id, turn_index, transcript, pitch_mean, pitch_std,
                rms_energy, jitter, shimmer, speaking_rate, pause_ratio, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id, turn_index, transcript, pitch_mean, pitch_std,
                rms_energy, jitter, shimmer, speaking_rate, pause_ratio, timestamp,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def insert_intervention(
    session_id: int,
    action: str,
    action_params: str,
    spoken_text: str,
    started_at: str,
) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO interventions (
                session_id, action, action_params, spoken_text, started_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, action, action_params, spoken_text, started_at),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def insert_feedback(
    intervention_id: int,
    outcome: str,
    recorded_at: str,
    user_preference_text: str | None = None,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO feedback (
                intervention_id, outcome, user_preference_text, recorded_at
            ) VALUES (?, ?, ?, ?)
            """,
            (intervention_id, outcome, user_preference_text, recorded_at),
        )
        conn.commit()
    finally:
        conn.close()


def insert_personality_note(category: str, note_text: str, created_at: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO personality_notes (category, note_text, created_at) VALUES (?, ?, ?)",
            (category, note_text, created_at),
        )
        conn.commit()
    finally:
        conn.close()


def get_personality_notes() -> list[str]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT note_text FROM personality_notes ORDER BY created_at ASC"
        ).fetchall()
    finally:
        conn.close()

    return [row["note_text"] for row in rows]
