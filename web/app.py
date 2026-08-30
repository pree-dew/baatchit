import asyncio
import base64
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from prosody.features import extract_features
from state_machine.core import SessionCore
from stt.transcribe import transcribe
from tts.speak import stream_speech
from web.audio_registry import discard_stream, get_stream, register_stream
from web.render import WEB_INTERVENTION_DISPATCH

app = FastAPI()


async def _stream_audio_response(stream_id: str) -> StreamingResponse:
    factory = get_stream(stream_id)
    if factory is None:
        return StreamingResponse(iter(()), status_code=404)

    async def body():
        try:
            async for chunk in factory():
                yield chunk
        finally:
            discard_stream(stream_id)

    return StreamingResponse(body(), media_type="audio/mpeg")


@app.get("/audio/tts/{stream_id}")
async def get_tts_audio(stream_id: str):
    return await _stream_audio_response(stream_id)


@app.get("/audio/music/{stream_id}")
async def get_music_audio(stream_id: str):
    return await _stream_audio_response(stream_id)

# music/soothing_images fetch once and should stay visible/audible until the
# user's next turn (or an explicit stop) -- unlike breathing/walk_timer,
# whose tick loop has a real, meaningful natural end.
LINGERING_ACTIONS = {"music", "soothing_images"}

EMPTY_FEATURES = {
    "pitch_mean": None,
    "pitch_std": None,
    "rms_energy": None,
    "jitter": None,
    "shimmer": None,
    "speaking_rate": None,
    "pause_ratio": None,
}


async def _run_intervention_with_stop_check(websocket: WebSocket, action: str, args: dict) -> bool:
    stop_event = asyncio.Event()

    def stop_check() -> bool:
        return stop_event.is_set()

    intervention_task = asyncio.create_task(
        WEB_INTERVENTION_DISPATCH[action](websocket, args, stop_check)
    )

    while not intervention_task.done():
        receive_task = asyncio.create_task(websocket.receive_json())
        done, pending = await asyncio.wait(
            {intervention_task, receive_task}, return_when=asyncio.FIRST_COMPLETED
        )

        if receive_task in done:
            message = receive_task.result()
            if message["type"] == "stop_intervention":
                stop_event.set()
        else:
            receive_task.cancel()

    return intervention_task.result()


async def _wait_for_audio_finished(websocket: WebSocket) -> None:
    while True:
        message = await websocket.receive_json()
        if message["type"] == "audio_finished":
            return


async def _process_turn(websocket: WebSocket, core: SessionCore, transcript: str, features: dict) -> bool:
    await websocket.send_json({"type": "intervention_ended", "stopped_early": False})
    await websocket.send_json({"type": "status", "value": "thinking"})

    turn_result = core.handle_turn(transcript, features)

    await websocket.send_json({
        "type": "transcript",
        "role": "assistant",
        "text": turn_result["spoken_text"],
    })

    await websocket.send_json({"type": "status", "value": "synthesizing_speech"})
    text = turn_result["spoken_text"]
    stream_id = register_stream(lambda: stream_speech(text))
    await websocket.send_json({
        "type": "audio",
        "url": f"/audio/tts/{stream_id}",
    })
    await _wait_for_audio_finished(websocket)

    if turn_result["closed"]:
        await websocket.send_json({
            "type": "session_closed",
            "outcome": turn_result["outcome"],
        })
        return True

    if "intervention_args" in turn_result:
        action = turn_result["action"]
        args = turn_result["intervention_args"]

        await websocket.send_json({
            "type": "intervention_started",
            "action": action,
            "args": args,
        })

        stopped_early = await _run_intervention_with_stop_check(websocket, action, args)

        core.record_intervention_result(action, args, turn_result["spoken_text"], stopped_early)

        if action not in LINGERING_ACTIONS or stopped_early:
            await websocket.send_json({
                "type": "intervention_ended",
                "stopped_early": stopped_early,
            })

    await websocket.send_json({"type": "status", "value": "listening"})
    return False


@app.websocket("/ws/session")
async def session_endpoint(websocket: WebSocket):
    await websocket.accept()
    core = SessionCore()

    try:
        while True:
            message = await websocket.receive_json()

            if message["type"] == "stop_intervention":
                await websocket.send_json({"type": "intervention_ended", "stopped_early": True})
                continue

            if message["type"] == "text_turn":
                transcript = message["text"]
                if await _process_turn(websocket, core, transcript, EMPTY_FEATURES):
                    break

            elif message["type"] == "audio_turn":
                await websocket.send_json({"type": "status", "value": "transcribing"})

                audio_bytes = base64.b64decode(message["data"])
                with tempfile.TemporaryDirectory() as tmp_dir:
                    webm_path = str(Path(tmp_dir) / "turn.webm")
                    wav_path = str(Path(tmp_dir) / "turn.wav")
                    Path(webm_path).write_bytes(audio_bytes)

                    subprocess.run(
                        ["ffmpeg", "-y", "-i", webm_path, wav_path],
                        check=True,
                        capture_output=True,
                    )

                    result = transcribe(wav_path)
                    transcript, words = result["text"], result["words"]

                    await websocket.send_json({
                        "type": "transcript",
                        "role": "user",
                        "text": transcript,
                    })

                    features = extract_features(wav_path, words)

                if await _process_turn(websocket, core, transcript, features):
                    break

    except WebSocketDisconnect:
        pass
