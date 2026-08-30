import asyncio
import random
import subprocess
import tempfile
from pathlib import Path
from typing import AsyncIterator

from audio.player import play_audio_interruptible

MOOD_TRACKS = {
    "calming": ["lFcSrYw-ARY", "DRFHklnN-SM", "2OEL4P1Rz04", "cDQ-krl38yE", "caAVbyTCptw"],
    "upbeat": ["Rg3YlUwSkUc", "q2ZtzNztDKc", "XzhQ-FefINM", "pIvf9bOPXIw", "qg3X8fKCtZo"],
    "instrumental": ["sAcj8me7wGI", "6X_OEUFV0v4", "L3joz294TVw", "oPVte6aMprI", "WPni755-Krg"],
}

_last_played: dict[str, str] = {}


def _pick_track(mood: str) -> str:
    candidates = MOOD_TRACKS[mood]
    last = _last_played.get(mood)
    choices = [v for v in candidates if v != last] or candidates
    video_id = random.choice(choices)
    _last_played[mood] = video_id
    return video_id


async def download_track(mood: str, stop_check) -> tuple[bytes | None, str]:
    video_id = _pick_track(mood)
    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = str(Path(tmp_dir) / "track.wav")

        process = subprocess.Popen(
            ["yt-dlp", "-x", "--audio-format", "wav", "-o", out_path, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        while process.poll() is None:
            if stop_check():
                process.terminate()
                await asyncio.get_event_loop().run_in_executor(None, process.wait)
                return None, url

            await asyncio.sleep(0.1)

        if not Path(out_path).exists():
            return None, url

        return Path(out_path).read_bytes(), url


async def stream_track(mood: str) -> AsyncIterator[bytes]:
    # No stop_check polling here: when the HTTP client (the <audio> element)
    # disconnects, Starlette's StreamingResponse calls aclose() on this
    # generator, which raises GeneratorExit at the current yield and runs
    # the finally block below -- that's what kills the subprocess.
    video_id = _pick_track(mood)
    url = f"https://www.youtube.com/watch?v={video_id}"

    process = await asyncio.create_subprocess_exec(
        "yt-dlp", "-x", "--audio-format", "mp3", "-o", "-", url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    try:
        while True:
            chunk = await process.stdout.read(4096)
            if not chunk:
                break
            yield chunk
    finally:
        if process.returncode is None:
            process.terminate()
            await process.wait()


async def play_music(mood: str, stop_check) -> bool:
    print("Getting a track ready for you...")
    audio_bytes, _url = await download_track(mood, stop_check)

    if audio_bytes is None:
        return True

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = str(Path(tmp_dir) / "playback.wav")
        Path(out_path).write_bytes(audio_bytes)
        return await play_audio_interruptible(out_path, stop_check)
