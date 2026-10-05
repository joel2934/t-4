"""Local speech-to-text powered by Faster-Whisper."""
from pathlib import Path
from typing import Dict


MODEL_CACHE_DIR = Path(__file__).resolve().parent / ".whisper_models"
ALLOWED_MODELS = {"tiny", "base"}


def transcribe(audio_path: Path, model_size: str = "tiny") -> Dict[str, str]:
    """Transcribe audio locally using the tiny or base Whisper model."""
    if model_size not in ALLOWED_MODELS:
        raise RuntimeError("Only the tiny and base Whisper models are available.")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Speech-to-text is not installed. Run: pip install -r requirements.txt"
        ) from exc

    try:
        model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            download_root=str(MODEL_CACHE_DIR),
        )
        segments, info = model.transcribe(str(audio_path), beam_size=5, vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return {"text": text, "language": info.language, "model": model_size}
    except Exception as exc:
        raise RuntimeError(
            f"Whisper could not load the {model_size} model. On first use it must "
            "download the model; check your internet connection and try again."
        ) from exc
