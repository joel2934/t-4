"""OpenRouter client for meeting analysis."""
import json
import os
import base64
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_TRANSCRIPTION_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_TRANSCRIPTION_MODEL = "openai/whisper-large-v3"


def _api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured. Set it and restart the API.")
    return key


def chat(messages: List[Dict[str, str]], *, json_output: bool = False) -> str:
    payload: Dict[str, Any] = {
        "model": os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
        "messages": messages,
        "temperature": 0.2,
    }
    if json_output:
        payload["response_format"] = {"type": "json_object"}
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {_api_key()}", "Content-Type": "application/json"},
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise RuntimeError(f"OpenRouter request failed: {detail}") from exc
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError("OpenRouter returned an unexpected response.") from exc
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("OpenRouter returned an empty response.")
    return content.strip()


def chat_json(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    try:
        result = json.loads(chat(messages, json_output=True))
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenRouter returned invalid JSON.") from exc
    if not isinstance(result, dict):
        raise RuntimeError("OpenRouter returned JSON that was not an object.")
    return result


def transcribe_audio(audio: bytes, audio_format: str) -> Dict[str, Any]:
    """Transcribe audio through OpenRouter's speech-to-text endpoint."""
    if not audio:
        raise RuntimeError("The uploaded recording is empty.")
    payload = {
        "model": os.getenv("OPENROUTER_TRANSCRIPTION_MODEL", DEFAULT_TRANSCRIPTION_MODEL),
        "input_audio": {
            "data": base64.b64encode(audio).decode("ascii"),
            "format": audio_format,
        },
    }
    try:
        response = requests.post(
            OPENROUTER_TRANSCRIPTION_URL,
            headers={"Authorization": f"Bearer {_api_key()}", "Content-Type": "application/json"},
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise RuntimeError(f"OpenRouter transcription failed: {detail}") from exc
    except ValueError as exc:
        raise RuntimeError("OpenRouter returned an invalid transcription response.") from exc
    if not isinstance(result, dict) or not isinstance(result.get("text"), str):
        raise RuntimeError("OpenRouter returned an invalid transcription response.")
    return result
