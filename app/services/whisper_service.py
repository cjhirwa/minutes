"""Thin wrapper around the Whisper model with lazy import and clear errors."""

_model = None


def _load_model(name: str = "small"):
    global _model
    if _model is not None:
        return _model

    try:
        import whisper
    except ImportError as e:
        raise RuntimeError(
            "Whisper library not installed. "
            "Install with: pip install openai-whisper"
        ) from e
    except Exception as e:
        raise RuntimeError(
            "Whisper library failed to initialize. "
            "This usually means PyTorch or ffmpeg is missing/misconfigured. "
            f"Error: {type(e).__name__}: {e}"
        ) from e

    try:
        _model = whisper.load_model(name)
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Whisper model '{name}'. "
            f"Error: {type(e).__name__}: {e}"
        ) from e

    return _model


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file and return the transcript text."""
    model = _load_model()
    try:
        result = model.transcribe(file_path)
        return result.get("text", "")
    except Exception as e:
        raise RuntimeError(f"Whisper transcription failed: {type(e).__name__}: {e}") from e