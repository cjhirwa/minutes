from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import summarization, transcription

app = FastAPI(title="Meeting Minutes AI")

origins = [
    "http://localhost:3000",  # your frontend URL
    "http://127.0.0.1:5500",  # e.g., live server
    "*",                      # allow all origins (use only for dev)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    transcription.router, prefix="/api/transcribe", tags=["transcription"]
)
app.include_router(
    summarization.router, prefix="/api/summarize", tags=["summarization"]
)


# add status endpoint
@app.get("/api/status")
async def get_status():
    return {"status": "ready"}


# add root endpoint
@app.get("/api/")
async def root():
    return {"message": "Welcome to the Meeting Minutes AI API"}
