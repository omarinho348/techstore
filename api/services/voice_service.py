"""Speech-to-text utilities powered by Faster-Whisper."""

import asyncio

from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")


def _transcribe(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path)
    return " ".join(segment.text for segment in segments).strip()


async def transcribe_audio(audio_path: str) -> str:
    """Convert recorded speech to text without blocking the async API loop."""

    return await asyncio.to_thread(_transcribe, audio_path)
