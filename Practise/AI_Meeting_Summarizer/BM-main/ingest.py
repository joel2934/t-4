"""
Transcript ingestion utilities.
Accepts plain text (or file content). Returns a transcript id saved in the store.
"""
from typing import Dict, Any
import store


def ingest_text(text: str, meta: Dict[str, Any] = None) -> str:
    """Save transcript text into store and return transcript id."""
    tid = store.save_transcript(text, meta=meta)
    return tid
