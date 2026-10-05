"""Embedding + chunking + similarity search for follow-up Q&A (light RAG)."""
import re
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """Split transcript text into overlapping word chunks."""
    words = re.split(r"\s+", text.strip())
    if not words:
        return []
    chunks = []
    step = max(chunk_size - overlap, 1)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """Embed a list of text chunks into vectors."""
    model = get_model()
    vectors = model.encode(chunks, convert_to_numpy=True)
    return vectors.tolist()


def embed_query(query: str) -> List[float]:
    model = get_model()
    return model.encode([query], convert_to_numpy=True)[0].tolist()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(a.dot(b) / denom)


def top_k_chunks(
    query: str,
    all_chunks: Dict[str, List[Dict]],
    k: int = 5,
) -> List[Dict]:
    """
    all_chunks: {transcript_id: [{"text": ..., "vector": [...]}, ...]}
    Returns top-k chunks across all transcripts, sorted by similarity.
    """
    q_vector = embed_query(query)
    scored = []
    for transcript_id, chunks in all_chunks.items():
        for chunk in chunks:
            score = cosine_similarity(q_vector, chunk["vector"])
            scored.append({
                "transcript_id": transcript_id,
                "text": chunk["text"],
                "score": score,
            })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]