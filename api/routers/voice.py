from pathlib import Path
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)

from api.services.voice_service import (
    transcribe_audio,
    text_to_speech,
)

from api.auth import get_current_customer
from api.models.customer import Customer

from api.services.chat_service import process_chat
from api.services.voice_service import transcribe_audio

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@router.post("")
async def voice_chat(

    audio: UploadFile = File(...),

    session_id: str = Form(...),

    current_customer: Customer = Depends(
        get_current_customer,
    ),

):

    filename = (
        f"{uuid.uuid4()}.webm"
    )

    filepath = UPLOAD_FOLDER / filename

    with open(filepath, "wb") as buffer:

        shutil.copyfileobj(
            audio.file,
            buffer,
        )

    transcript = await transcribe_audio(
        str(filepath),
    )

    response = await process_chat(

        session_id=session_id,

        message=transcript,

        current_customer=current_customer,

    )

    filepath.unlink()

    audio_file = await text_to_speech(
    response.response,
    )

    return {

    "transcript": transcript,

    "response": response.response,

    "audio_url": f"/audio/{audio_file}",

    }