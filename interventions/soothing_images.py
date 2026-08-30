import base64
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

THEME_URLS = {
    "nature": "https://loremflickr.com/1600/900/nature,calm",
    "ocean": "https://loremflickr.com/1600/900/ocean,peaceful",
    "soft_abstract": "https://loremflickr.com/1600/900/abstract,soft,pastel",
}

_CHUNK_SIZE = 4096


def _convert_to_png(image_bytes: bytes, stop_check) -> bytes | None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        src_path = Path(tmp_dir) / "source"
        png_path = Path(tmp_dir) / "converted.png"
        src_path.write_bytes(image_bytes)

        process = subprocess.Popen(
            ["sips", "-s", "format", "png", str(src_path), "--out", str(png_path)],
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
                    return None

        if not png_path.exists():
            return None

        return png_path.read_bytes()


def _display_inline(png_bytes: bytes) -> None:
    encoded = base64.b64encode(png_bytes)
    chunks = [encoded[i : i + _CHUNK_SIZE] for i in range(0, len(encoded), _CHUNK_SIZE)]

    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        more = 0 if is_last else 1
        control = f"a=T,f=100,m={more}" if i == 0 else f"m={more}"
        sys.stdout.write(f"\x1b_G{control};{chunk.decode('ascii')}\x1b\\")

    sys.stdout.flush()


def show_soothing_image(theme: str, stop_check) -> bool:
    if stop_check():
        return True

    url = THEME_URLS[theme]
    with urllib.request.urlopen(url) as response:
        image_bytes = response.read()

    if stop_check():
        return True

    png_bytes = _convert_to_png(image_bytes, stop_check)
    if png_bytes is None:
        return True

    _display_inline(png_bytes)
    return False
