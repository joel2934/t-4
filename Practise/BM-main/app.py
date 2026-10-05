"""FastAPI backend for the AI Meeting Summarizer & Action-Item Tracker.

Run with: uvicorn app:app --reload
Interactive API documentation: http://127.0.0.1:8000/docs
"""
from io import BytesIO
from pathlib import Path
import tempfile
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import extractor
import ingest
import llm
import store
import summarizer
import speech_to_text
import tracker

app = FastAPI(title="AI Meeting Summarizer & Action-Item Tracker", version="1.0.0")


class IngestRequest(BaseModel):
    text: str = Field(min_length=1)
    meta: Optional[Dict[str, Any]] = None


class TranscriptRequest(BaseModel):
    transcript_id: str = Field(min_length=1)


class ActionUpdateRequest(BaseModel):
    action_id: str = Field(min_length=1)
    status: str = Field(min_length=1)


def get_transcript_or_404(transcript_id: str) -> Dict[str, Any]:
    try:
        return store.get_transcript(transcript_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Transcript not found") from exc


@app.get("/")
def home():
    return {"message": "AI Meeting Summarizer API is running.", "docs": "/docs"}


@app.post("/ingest")
def api_ingest(payload: IngestRequest):
    return {"transcript_id": ingest.ingest_text(payload.text, meta=payload.meta)}


@app.post("/transcribe")
async def api_transcribe(
    file: UploadFile = File(...), model: str = Form("tiny"),
):
    """Convert an uploaded recording into text using local Faster-Whisper."""
    if model not in speech_to_text.ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail="Only tiny and base Whisper models are supported")
    suffix = Path(file.filename or "recording.wav").suffix or ".wav"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(await file.read())
        result = speech_to_text.transcribe(temp_path, model)
        if not result["text"]:
            raise HTTPException(status_code=422, detail="No speech was detected in the recording")
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


@app.post("/summarize")
def api_summarize(payload: TranscriptRequest):
    record = get_transcript_or_404(payload.transcript_id)
    try:
        summary = summarizer.summarize_text(record.get("text", ""))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    store.save_summary(payload.transcript_id, summary)
    return {"transcript_id": payload.transcript_id, "summary": summary,
            "eval": summarizer.evaluate_summary(summary, record.get("text", ""))}


@app.post("/extract_actions")
def api_extract_actions(payload: TranscriptRequest):
    record = get_transcript_or_404(payload.transcript_id)
    try:
        actions = extractor.extract_actions(record.get("text", ""))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    store.save_actions(payload.transcript_id, actions)
    return {"transcript_id": payload.transcript_id, "actions": actions}


@app.get("/query")
def api_query(q: str = Query(min_length=1)):
    top_chunks = store.search_similar_chunks(q, top_k=5)
    if not top_chunks:
        return {"query": q, "answer": "No relevant meetings found.", "sources": []}

    context = "\n\n".join(f"[{c['transcript_id']}] {c['text']}" for c in top_chunks)
    answer = llm.chat([
        {"role": "system", "content": (
            "Answer the user's question using only the provided meeting excerpts. "
            "If the answer isn't in the excerpts, say you don't know."
        )},
        {"role": "user", "content": f"Excerpts:\n{context}\n\nQuestion: {q}"},
    ])
    return {"query": q, "answer": answer, "sources": top_chunks}


@app.post("/track")
def api_track(payload: TranscriptRequest):
    get_transcript_or_404(payload.transcript_id)
    try:
        actions = store.get_actions(payload.transcript_id).get("actions", [])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="No extracted actions found for this transcript") from exc
    return {"created_action_ids": tracker.capture_actions(payload.transcript_id, actions)}


@app.post("/track/update")
def api_track_update(payload: ActionUpdateRequest):
    if not tracker.set_action_status(payload.action_id, payload.status):
        raise HTTPException(status_code=404, detail="Action item not found")
    return {"action_id": payload.action_id, "status": payload.status, "ok": True}


@app.get("/track/list")
def api_track_list(status: Optional[str] = None, transcript_id: Optional[str] = None):
    return {"actions": tracker.list_actions(status=status, transcript_id=transcript_id)}


@app.get("/export")
def api_export(transcript_id: str = Query(min_length=1)):
    get_transcript_or_404(transcript_id)
    try:
        summary = store.get_summary(transcript_id).get("summary")
    except FileNotFoundError:
        summary = None
    try:
        actions = store.get_actions(transcript_id).get("actions", [])
    except FileNotFoundError:
        actions = []
    lines = [f"# Meeting Summary (Transcript {transcript_id})", "", "## Summary", summary or "(no summary available)", "", "## Action Items"]
    if actions:
        lines.extend(f"- **{a.get('task')}** — Owner: {a.get('owner') or 'Unassigned'}, Deadline: {a.get('deadline') or 'No deadline'}" for a in actions)
    else:
        lines.append("(no actions found)")
    content = "\n".join(lines).encode("utf-8")
    return StreamingResponse(BytesIO(content), media_type="text/markdown",
                             headers={"Content-Disposition": f'attachment; filename="export_{transcript_id}.md"'})
