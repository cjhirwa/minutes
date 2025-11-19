import os
from pathlib import Path
from typing import Set

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.whisper_service import transcribe_audio

router = APIRouter()

# Configure allowed audio formats
ALLOWED_EXTENSIONS: Set[str] = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"}
MAX_FILE_SIZE: int = 25 * 1024 * 1024  # 25MB


@router.post("/")
async def transcribe(file: UploadFile = File(...)):
    print("Received file for transcription:", file.filename)
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required"
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file contents
    contents = await file.read()

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Create temp directory
    tmp_dir = Path("temp")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Use secure filename (prevent path traversal)
    safe_filename = Path(file.filename).name
    file_path = tmp_dir / safe_filename

    try:
        # Write file asynchronously (or at least in a way that doesn't block too long)
        with open(file_path, "wb") as f:
            f.write(contents)

        # Transcribe audio
        text = transcribe_audio(str(file_path))

        return {"transcript": text}

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during transcription",
        )
    finally:
        # Always clean up the temporary file
        if file_path.exists():
            try:
                os.unlink(file_path)
            except Exception:
                pass  # Log this in production
