import baseline.welford as welford
from db import db as db_module


def get_baseline(feature_name: str) -> tuple[int, float, float]:
    conn = db_module.get_connection()
    try:
        row = conn.execute(
            "SELECT count, mean, m2 FROM user_baseline WHERE feature_name = ?",
            (feature_name,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return 0, 0.0, 0.0
    return row["count"], row["mean"], row["m2"]


def update_baseline(feature_name: str, new_value: float) -> None:
    count, mean, m2 = get_baseline(feature_name)
    count, mean, m2 = welford.update(count, mean, m2, new_value)

    conn = db_module.get_connection()
    try:
        conn.execute(
            """
            INSERT INTO user_baseline (feature_name, count, mean, m2)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(feature_name) DO UPDATE SET
                count = excluded.count,
                mean = excluded.mean,
                m2 = excluded.m2
            """,
            (feature_name, count, mean, m2),
        )
        conn.commit()
    finally:
        conn.close()


def get_zscore(feature_name: str, value: float) -> float | None:
    count, mean, m2 = get_baseline(feature_name)
    baseline_mean, baseline_std = welford.finalize(count, mean, m2)

    if baseline_std is None or baseline_std == 0:
        return None

    return (value - baseline_mean) / baseline_std
