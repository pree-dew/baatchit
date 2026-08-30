"""Central configuration: constants, paths, and API keys.

Every other module should import values from here rather than hardcoding
them locally -- a mismatch (e.g. SAMPLE_RATE used for recording vs. analysis)
produces silently wrong numbers, not an error.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "voice_companion.db"
RECORDINGS_DIR = DATA_DIR / "recordings"

# --- audio ---
# 16000 Hz is required by Silero VAD and is sufficient for pitch/intensity/
# jitter-shimmer analysis -- one sample rate throughout avoids resampling
# audio more than once between recording and analysis.
SAMPLE_RATE = 16000

# --- API keys (loaded from environment / .env) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# --- session state-machine tuning (used starting Stage 11) ---
AROUSAL_DROP_THRESHOLD = 0.25  # fraction drop from peak arousal that can trigger a check-in
CHECK_IN_TIMEOUT_SECONDS = 180  # fallback: force check-in after this long post-intervention
CHECK_IN_TIMEOUT_TURNS = 4  # fallback: force check-in after this many user turns post-intervention
