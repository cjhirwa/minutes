import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import summarization, transcription
from app.services.whisper_service import _load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Preload the Whisper model
    print("Preloading Whisper model...")
    try:
        _load_model("small")
        print("Whisper model loaded successfully!")
    except Exception as e:
        print(f"Warning: Failed to preload Whisper model: {e}")

    yield

    # Shutdown: cleanup if needed
    pass


app = FastAPI(lifespan=lifespan, title="Meeting Minutes AI")

# Mount static folder
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
app.mount("/web", StaticFiles(directory=static_path, html=True), name="static")

# API routers
app.include_router(
    transcription.router, prefix="/api/transcribe", tags=["transcription"]
)
app.include_router(
    summarization.router, prefix="/api/summarize", tags=["summarization"]
)


# Status endpoint
@app.get("/api/status")
async def get_status():
    return {"status": "ready"}


# Root redirect to frontend
from fastapi.responses import RedirectResponse


@app.get("/")
async def root():
    return RedirectResponse(url="/web/index.html")
