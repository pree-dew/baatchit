import random
import subprocess
import tempfile
from pathlib import Path

from audio.player import play_audio_interruptible

MOOD_TRACKS = {
    "calming": ["lFcSrYw-ARY", "DRFHklnN-SM", "2OEL4P1Rz04", "cDQ-krl38yE", "caAVbyTCptw"],
    "upbeat": ["Rg3YlUwSkUc", "q2ZtzNztDKc", "XzhQ-FefINM", "pIvf9bOPXIw", "qg3X8fKCtZo"],
    "instrumental": ["sAcj8me7wGI", "6X_OEUFV0v4", "L3joz294TVw", "oPVte6aMprI", "WPni755-Krg"],
}

_last_played: dict[str, str] = {}


def play_music(mood: str, stop_check) -> bool:
    candidates = MOOD_TRACKS[mood]
    last = _last_played.get(mood)
    choices = [v for v in candidates if v != last] or candidates
    video_id = random.choice(choices)
    _last_played[mood] = video_id

    url = f"https://www.youtube.com/watch?v={video_id}"

    print("Getting a track ready for you...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = str(Path(tmp_dir) / "track.wav")

        process = subprocess.Popen(
            ["yt-dlp", "-x", "--audio-format", "wav", "-o", out_path, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        while True:
            try:
                process.wait(timeout=0.1)
                break
            except subprocess.TimeoutExpired:
                if stop_check():
                    process.terminate()
                    process.wait()
                    return True

        if not Path(out_path).exists():
            return True

        return play_audio_interruptible(out_path, stop_check)
