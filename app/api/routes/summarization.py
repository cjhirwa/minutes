from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_service import MeetingMinutesGenerator

router = APIRouter()


class TranscriptRequest(BaseModel):
    transcript: str


@router.post("/")
def summarize(request: TranscriptRequest):
    generator = MeetingMinutesGenerator()
    minute = generator.generate_minutes(request.transcript)
    return {"minutes": minute}
