import random

from db import db as db_module

ALPHA = 0.3
EPSILON = 0.1

ALL_INTERVENTION_TYPES = [
    "breathing",
    "music",
    "walk_timer",
    "distraction",
    "journal",
    "soothing_images",
]


def get_score(intervention_type: str, emotion: str) -> tuple[float, int]:
    conn = db_module.get_connection()
    try:
        row = conn.execute(
            "SELECT score, count FROM intervention_scores WHERE intervention_type = ? AND emotion = ?",
            (intervention_type, emotion),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return 0.5, 0
    return row["score"], row["count"]


def update_score(intervention_type: str, emotion: str, outcome: float) -> None:
    current_score, count = get_score(intervention_type, emotion)
    new_score = ALPHA * outcome + (1 - ALPHA) * current_score

    conn = db_module.get_connection()
    try:
        conn.execute(
            """
            INSERT INTO intervention_scores (intervention_type, emotion, score, count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(intervention_type, emotion) DO UPDATE SET
                score = excluded.score,
                count = excluded.count
            """,
            (intervention_type, emotion, new_score, count + 1),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_scores() -> list[dict]:
    conn = db_module.get_connection()
    try:
        rows = conn.execute(
            "SELECT intervention_type, emotion, score, count FROM intervention_scores WHERE count > 0"
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "intervention_type": r["intervention_type"],
            "emotion": r["emotion"],
            "score": r["score"],
            "count": r["count"],
        }
        for r in rows
    ]


def choose_intervention(emotion: str) -> str:
    if random.random() < EPSILON:
        return random.choice(ALL_INTERVENTION_TYPES)

    scored = [(t, get_score(t, emotion)[0]) for t in ALL_INTERVENTION_TYPES]
    best_type, _ = max(scored, key=lambda pair: pair[1])
    return best_type
