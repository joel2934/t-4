"""
Simple file-based store for transcripts, summaries, and action items.
This is a small persistence layer for the prototype. It stores JSON files under ./data/.
Replace or extend with a DB or vector store for production.
"""
import os
import json
import uuid
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
SUMMARY_DIR = os.path.join(DATA_DIR, "summaries")
ACTIONS_DIR = os.path.join(DATA_DIR, "actions")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")

for d in (TRANSCRIPT_DIR, SUMMARY_DIR, ACTIONS_DIR, EMBEDDINGS_DIR):
    os.makedirs(d, exist_ok=True)


def _write_json(path: str, obj: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_transcript(text: str, meta: Dict[str, Any] = None) -> str:
    tid = str(uuid.uuid4())
    rec = {
        "id": tid,
        "text": text,
        "meta": meta or {},
    }
    _write_json(os.path.join(TRANSCRIPT_DIR, f"{tid}.json"), rec)
    _save_embeddings(tid, text)
    return tid


def _save_embeddings(tid: str, text: str) -> None:
    import embeddings
    chunks = embeddings.chunk_text(text)
    if not chunks:
        return
    vectors = embeddings.embed_chunks(chunks)
    rec = {
        "transcript_id": tid,
        "chunks": [{"text": c, "vector": v} for c, v in zip(chunks, vectors)],
    }
    _write_json(os.path.join(EMBEDDINGS_DIR, f"{tid}.json"), rec)


def get_all_embeddings() -> Dict[str, List[Dict]]:
    result = {}
    for fname in os.listdir(EMBEDDINGS_DIR):
        if not fname.endswith(".json"):
            continue
        rec = _read_json(os.path.join(EMBEDDINGS_DIR, fname))
        result[rec["transcript_id"]] = rec["chunks"]
    return result


def get_transcript(tid: str) -> Dict[str, Any]:
    path = os.path.join(TRANSCRIPT_DIR, f"{tid}.json")
    return _read_json(path)


def save_summary(tid: str, summary: str) -> None:
    rec = {"transcript_id": tid, "summary": summary}
    _write_json(os.path.join(SUMMARY_DIR, f"{tid}.json"), rec)


def get_summary(tid: str) -> Dict[str, Any]:
    path = os.path.join(SUMMARY_DIR, f"{tid}.json")
    return _read_json(path)


def save_actions(tid: str, actions: List[Dict[str, Any]]) -> None:
    rec = {"transcript_id": tid, "actions": actions}
    _write_json(os.path.join(ACTIONS_DIR, f"{tid}.json"), rec)


def get_actions(tid: str) -> Dict[str, Any]:
    path = os.path.join(ACTIONS_DIR, f"{tid}.json")
    return _read_json(path)


def list_transcripts() -> List[str]:
    return [f[:-5] for f in os.listdir(TRANSCRIPT_DIR) if f.endswith('.json')]

# Simple "vector store" placeholder: returns transcript ids that contain the query tokens
# Replace with real embeddings + nearest-neighbor search later

def search_similar_chunks(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Real semantic search: embeds the query and finds the closest transcript chunks."""
    import embeddings
    all_chunks = get_all_embeddings()
    return embeddings.top_k_chunks(query, all_chunks, k=top_k)
