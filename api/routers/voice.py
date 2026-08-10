from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from api.auth import get_current_customer
from api.models.customer import Customer
from api.services.voice_service import transcribe_audio

router = APIRouter(prefix="/voice", tags=["Voice"])

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@router.post("/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    current_customer: Customer = Depends(get_current_customer),
):
    """Persist a recording privately and return its Faster-Whisper transcript."""

    suffix = Path(audio.filename or "recording.webm").suffix or ".webm"
    filename = f"{session_id}-{uuid.uuid4()}{suffix}"
    file_path = UPLOAD_FOLDER / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:
        transcript = await transcribe_audio(str(file_path))
    except Exception as error:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Voice transcription failed.",
        ) from error

    if not transcript:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="No speech was detected in the recording.",
        )

    return {"transcript": transcript, "audio_file": filename}
