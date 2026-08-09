"""
api/services/voice_service.py

Speech-to-Text using Faster Whisper.
"""
import os
import uuid

from openai import AsyncOpenAI
from faster_whisper import WhisperModel
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


# ================================================================
# LOAD MODEL
# ================================================================

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8",
)

# ================================================================
# TRANSCRIBE AUDIO
# ================================================================

async def transcribe_audio(
    audio_path: str,
) -> str:
    """
    Convert speech into text.
    """

    segments, _ = model.transcribe(
        audio_path,
    )

    transcript = " ".join(
        segment.text
        for segment in segments
    ).strip()

    return transcript

# ================================================================
# TEXT TO SPEECH
# ================================================================

async def text_to_speech(
    text: str,
) -> str:
    """
    Convert assistant text into speech.
    Returns the generated mp3 filename.
    """

    filename = f"{uuid.uuid4()}.mp3"

    output_path = os.path.join(
        "audio",
        filename,
    )

    response = await client.audio.speech.create(
        model="gpt-5.4-mini",
        voice="alloy",
        input=text,
    )

    await response.stream_to_file(
        output_path,
    )

    return filename