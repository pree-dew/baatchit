import base64

from fastapi import WebSocket

from interventions.breathing import run_breathing
from interventions.distraction import run_distraction
from interventions.journal import run_journal
from interventions.music import stream_track
from interventions.soothing_images import fetch_and_convert
from interventions.walk_timer import run_walk_timer
from web.audio_registry import register_stream


async def render_breathing_ws(websocket: WebSocket, args: dict, stop_check) -> bool:
    async for state in run_breathing(args["pace"]):
        if stop_check():
            return True
        await websocket.send_json({"type": "intervention_tick", "state": state})
    return False


async def render_walk_timer_ws(websocket: WebSocket, args: dict, stop_check) -> bool:
    async for state in run_walk_timer(args["duration_minutes"]):
        if stop_check():
            return True
        await websocket.send_json({"type": "intervention_tick", "state": state})
    return False


async def render_music_ws(websocket: WebSocket, args: dict, stop_check) -> bool:
    mood = args["mood"]
    stream_id = register_stream(lambda: stream_track(mood))

    await websocket.send_json({
        "type": "intervention_media",
        "media_type": "audio",
        "url": f"/audio/music/{stream_id}",
    })
    return False


async def render_soothing_image_ws(websocket: WebSocket, args: dict, stop_check) -> bool:
    png_bytes = await fetch_and_convert(args["theme"], stop_check)

    if png_bytes is None:
        return True

    await websocket.send_json({
        "type": "intervention_media",
        "media_type": "image",
        "data": base64.b64encode(png_bytes).decode("ascii"),
    })
    return False


WEB_INTERVENTION_DISPATCH = {
    "breathing": render_breathing_ws,
    "walk_timer": render_walk_timer_ws,
    "music": render_music_ws,
    "distraction": lambda websocket, args, stop_check: run_distraction(args["style"], stop_check),
    "journal": lambda websocket, args, stop_check: run_journal(args["prompt_theme"], stop_check),
    "soothing_images": render_soothing_image_ws,
}
