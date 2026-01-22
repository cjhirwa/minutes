_model = None


def _load_model(name: str = "small"):
    """Load the faster-whisper model (only if not already loaded)."""
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

    try:
        device = "cuda" if _gpu_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        _model = WhisperModel(name, device=device, compute_type=compute_type)
        return _model
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Faster-Whisper model '{name}': {e}"
        ) from e


def get_model():
    """Get the loaded model instance."""
    if _model is None:
        _load_model()
    return _model


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file using faster-whisper."""
    model = get_model()  # ← More explicit: "get" vs "load"

    try:
        segments, info = model.transcribe(
            file_path,
            beam_size=1,
            vad_filter=True,
        )
        text = "".join(s.text for s in segments)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Whisper transcription failed: {e}") from e


def _gpu_available():
    """Return True if PyTorch detects a CUDA GPU."""
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False