PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sessions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at        TEXT NOT NULL,
    ended_at          TEXT,
    baseline_arousal  REAL,
    peak_arousal      REAL,
    closing_arousal   REAL
);

CREATE TABLE IF NOT EXISTS utterances (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id     INTEGER NOT NULL REFERENCES sessions(id),
    turn_index     INTEGER NOT NULL,
    transcript     TEXT NOT NULL,
    pitch_mean     REAL,
    pitch_std      REAL,
    rms_energy     REAL,
    jitter         REAL,
    shimmer        REAL,
    speaking_rate  REAL,
    pause_ratio    REAL,
    timestamp      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interventions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id     INTEGER NOT NULL REFERENCES sessions(id),
    action         TEXT NOT NULL,
    action_params  TEXT,
    spoken_text    TEXT,
    started_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    intervention_id       INTEGER NOT NULL REFERENCES interventions(id),
    outcome               TEXT NOT NULL,
    user_preference_text  TEXT,
    recorded_at           TEXT NOT NULL
);

-- Single-user demo: one row per prosody feature (pitch_mean, rms_energy,
-- etc.), no user_id column. A multi-user version would add user_id here
-- and to the primary key.
CREATE TABLE IF NOT EXISTS user_baseline (
    feature_name  TEXT PRIMARY KEY,
    count         INTEGER NOT NULL,
    mean          REAL NOT NULL,
    m2            REAL NOT NULL
);

-- Free-text notes accumulated over time, persisted across sessions.
-- category distinguishes intervention-preference notes ("dislikes being
-- told to 'just breathe'") from feedback-interpretation notes ("tends to
-- downplay how much something helped").
CREATE TABLE IF NOT EXISTS personality_notes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    category      TEXT NOT NULL,
    note_text     TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

-- One row per (intervention_type, emotion) pair. score is an exponential
-- moving average of past outcomes (1.0 = helped, 0.0 = not_helped), giving
-- more weight to recent feedback than old feedback. count is tracked for
-- transparency only (not required by the EMA formula itself) so low-
-- confidence scores built from very few observations can be identified.
CREATE TABLE IF NOT EXISTS intervention_scores (
    intervention_type  TEXT NOT NULL,
    emotion             TEXT NOT NULL,
    score               REAL NOT NULL,
    count               INTEGER NOT NULL,
    PRIMARY KEY (intervention_type, emotion)
);
