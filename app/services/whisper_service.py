"""Thin wrapper around the faster-whisper model with lazy import and clear errors."""

_model = None


def _load_model(name: str = "small"):
    """
    Lazy-load the faster-whisper model.
    """
    global _model
    if _model is not None:
        return _model

    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError(
            "faster-whisper is not installed. "
            "Install with: pip install faster-whisper"
        ) from e
    except Exception as e:
        raise RuntimeError(
            "Faster-Whisper failed to initialize. "
            "This usually means ffmpeg is missing or your environment is broken. "
            f"Error: {type(e).__name__}: {e}"
        ) from e

    try:
        # auto-select device; CPU gets int8 for speed
        device = "cuda" if _gpu_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        _model = WhisperModel(
            name,
            device=device,
            compute_type=compute_type,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Faster-Whisper model '{name}'. "
            f"Error: {type(e).__name__}: {e}"
        ) from e

    return _model


def _gpu_available():
    """Return True if PyTorch detects a CUDA GPU."""
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file using faster-whisper and return the transcript text.
    """
    model = _load_model()

    try:
        segments, info = model.transcribe(
            file_path,
            beam_size=1,     # fast decoding
            vad_filter=True, # skip silence, improves speed
        )

        # Collect segments into a single string
        text = "".join(s.text for s in segments)
        return text.strip()

    except Exception as e:
        raise RuntimeError(
            f"Whisper transcription failed: {type(e).__name__}: {e}"
        ) from e
