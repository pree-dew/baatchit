import uuid
from typing import AsyncIterator, Callable

_STREAMS: dict[str, Callable[[], AsyncIterator[bytes]]] = {}


def register_stream(factory: Callable[[], AsyncIterator[bytes]]) -> str:
    stream_id = uuid.uuid4().hex
    _STREAMS[stream_id] = factory
    return stream_id


def get_stream(stream_id: str) -> Callable[[], AsyncIterator[bytes]] | None:
    return _STREAMS.get(stream_id)


def discard_stream(stream_id: str) -> None:
    _STREAMS.pop(stream_id, None)
