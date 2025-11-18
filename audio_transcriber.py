# audio_transcriber.py

import os
import tempfile
from typing import Optional

import whisper  # from the openai-whisper package


_MODEL = None


def _get_model(model_name: str = "tiny"):
    """
    Load the Whisper 'tiny' model from the local whisper_models directory.
    This avoids online downloads and works on all teammates' computers.
    """
    global _MODEL
    if _MODEL is None:
        base_dir = os.path.dirname(__file__)
        model_dir = os.path.join(base_dir, "whisper_models")
        _MODEL = whisper.load_model(model_name, download_root=model_dir)
    return _MODEL


def transcribe_audio_file(uploaded_file, language: Optional[str] = None) -> str:
    if language is None:
        language = "en"  # Always assume English

    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        model = _get_model()
        result = model.transcribe(tmp_path, language=language)
        text = result.get("text", "").strip()
        return text
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
