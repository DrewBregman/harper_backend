# forms.py (or a new file, e.g. voice.py in the same directory)

import openai
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from config import OPENAI_API_KEY
import os
import tempfile

router = APIRouter()

openai.api_key = OPENAI_API_KEY

@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    """
    Receive an audio file, save it temporarily, and call OpenAI Whisper to transcribe.
    Returns { "transcript": "..." } on success.
    """
    # Validate file type if needed
    # e.g. if file.content_type not in ["audio/wav", "audio/mpeg", "audio/webm"]: ...
    try:
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Use openai.Audio.transcribe
        # If using 'whisper-1', you can do:
        # transcript_data = openai.Audio.transcribe("whisper-1", open(tmp_path, "rb"))
        # OR with the newer approach "openai.Audio.transcribe"
        # For older openai libs, might be openai.Audio.create(...)
        # We'll show the current approach:

        transcript_data = openai.Audio.transcribe(
            model="whisper-1",
            file=open(tmp_path, "rb"),
        )
        # transcript_data is typically { "text": "... recognized text ..." }
        recognized_text = transcript_data.get("text", "")

        # Cleanup
        os.remove(tmp_path)

        return {"transcript": recognized_text}

    except Exception as e:
        # If something fails, remove the file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
