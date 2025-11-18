# audio_transcriber.py

import os
import tempfile
from typing import Optional

import whisper  # from the openai-whisper package


_MODEL = None


_MODEL = None

def _get_model(model_name: str = "tiny"):
    """
    Load Whisper model from a local folder inside the project (whisper_models)
    so it doesn't need to download anything at runtime.
    We use the smallest model ('tiny') for faster, lighter inference.
    """
    global _MODEL
    if _MODEL is None:
        base_dir = os.path.dirname(__file__)
        model_dir = os.path.join(base_dir, "whisper_models")
        _MODEL = whisper.load_model(model_name, download_root=model_dir)
    return _MODEL


def transcribe_audio_file(uploaded_file, language: Optional[str] = None) -> str:
    """
    Take a file-like object (Streamlit upload or similar),
    save it to a temp file, run Whisper, and return the transcript text.
    """
    # 1. Save the uploaded file to a temporary path
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # 2. Load model
        model = _get_model()

        # 3. Call Whisper
        # If language is None, Whisper will try to detect it.
        result = model.transcribe(tmp_path, language=language)

        # 4. Extract text
        text = result.get("text", "").strip()
        return text

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
