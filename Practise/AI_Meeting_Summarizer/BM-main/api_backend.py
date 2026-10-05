"""
FastAPI backend for the AI Meeting Summarizer & Action-Item Tracker.
Endpoints:
- POST /ingest -> accepts raw text, returns transcript_id
- POST /summarize -> {transcript_id} -> returns summary
- POST /extract_actions -> {transcript_id} -> returns extracted actions
- GET /query -> ?q=... -> returns list of transcript ids relevant (placeholder search)
- POST /track -> {transcript_id} captures actions into tracker
- POST /track/update -> {action_id, status} updates status
- GET /track/list -> list actions (optionally ?status=open)
- GET /export -> export summary + actions for transcript_id as markdown

Run: uvicorn api_backend:app --reload
"""
from pathlib import Path
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import ingest, summarizer, extractor, store, tracker, speech_to_text
import os

app = FastAPI(title="ByteMe Meeting Summarizer", version="1.0")


# Pydantic models
class IngestRequest(BaseModel):
    text: str
    meta: Optional[Dict[str, Any]] = None


class SummarizeRequest(BaseModel):
    transcript_id: str


class ExtractActionsRequest(BaseModel):
    transcript_id: str


class TrackRequest(BaseModel):
    transcript_id: str


class UpdateActionRequest(BaseModel):
    action_id: str
    status: str


@app.post("/transcribe")
async def api_transcribe(file: UploadFile = File(...), model: str = Form("tiny")):
    """Convert an uploaded or browser-recorded audio file using local Faster-Whisper."""
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


# Endpoints
@app.post("/ingest")
def api_ingest(req: IngestRequest):
    """Ingest a transcript and store it."""
    if not req.text:
        raise HTTPException(status_code=400, detail="text is required")
    tid = ingest.ingest_text(req.text, meta=req.meta)
    return {"transcript_id": tid}


@app.post("/summarize")
def api_summarize(req: SummarizeRequest):
    """Summarize a transcript."""
    if not req.transcript_id:
        raise HTTPException(status_code=400, detail="transcript_id required")
    try:
        rec = store.get_transcript(req.transcript_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    text = rec.get("text", "")
    try:
        summary = summarizer.summarize_text(text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    store.save_summary(req.transcript_id, summary)
    eval_info = summarizer.evaluate_summary(summary, text)
    return {
        "transcript_id": req.transcript_id,
        "summary": summary,
        "eval": eval_info,
    }


@app.post("/extract_actions")
def api_extract_actions(req: ExtractActionsRequest):
    """Extract action items from a transcript."""
    if not req.transcript_id:
        raise HTTPException(status_code=400, detail="transcript_id required")
    try:
        rec = store.get_transcript(req.transcript_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    text = rec.get("text", "")
    try:
        actions = extractor.extract_actions(text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    store.save_actions(req.transcript_id, actions)
    return {"transcript_id": req.transcript_id, "actions": actions}


@app.get("/query")
def api_query(q: Optional[str] = None):
    """Search transcripts by query string."""
    if not q:
        raise HTTPException(status_code=400, detail="q parameter required")
    hits = store.search_transcripts(q)
    results = []
    for tid in hits:
        try:
            t = store.get_transcript(tid)
            results.append({
                "transcript_id": tid,
                "meta": t.get("meta"),
                "snippet": t.get("text")[:400],
            })
        except Exception:
            pass
    return {"query": q, "results": results}


@app.post("/track")
def api_track(req: TrackRequest):
    """Capture extracted actions into the tracker."""
    if not req.transcript_id:
        raise HTTPException(status_code=400, detail="transcript_id required")
    try:
        actions_rec = store.get_actions(req.transcript_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No actions found for this transcript")
    
    actions = actions_rec.get("actions", [])
    ids = tracker.capture_actions(req.transcript_id, actions)
    return {"created_action_ids": ids}


@app.post("/track/update")
def api_track_update(req: UpdateActionRequest):
    """Update the status of an action item."""
    if not req.action_id or not req.status:
        raise HTTPException(status_code=400, detail="action_id and status required")
    ok = tracker.set_action_status(req.action_id, req.status)
    return {"action_id": req.action_id, "status": req.status, "ok": ok}


@app.get("/track/list")
def api_track_list(status: Optional[str] = None):
    """List all tracked actions, optionally filtered by status."""
    res = tracker.list_actions(status=status)
    return {"actions": res}


@app.get("/export")
def api_export(transcript_id: str):
    """Export summary and actions as markdown."""
    if not transcript_id:
        raise HTTPException(status_code=400, detail="transcript_id required")
    
    summ = None
    try:
        summ = store.get_summary(transcript_id).get("summary")
    except Exception:
        summ = None
    
    acts = None
    try:
        acts = store.get_actions(transcript_id).get("actions", [])
    except Exception:
        acts = []
    
    md_lines = []
    md_lines.append(f"# Meeting Summary (Transcript {transcript_id})\n")
    if summ:
        md_lines.append("## Summary\n")
        md_lines.append(summ)
        md_lines.append("\n")
    
    if acts:
        md_lines.append("## Action Items\n")
        for a in acts:
            owner = a.get("owner", "Unassigned")
            deadline = a.get("deadline", "No deadline")
            task = a.get("task", "")
            md_lines.append(f"- [ ] **{task}** (Owner: {owner}, Due: {deadline})\n")
    
    md_content = "".join(md_lines)
    
    # Write to temp file and return
    export_path = os.path.join(os.path.dirname(__file__), f"export_{transcript_id}.md")
    with open(export_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return FileResponse(export_path, media_type="text/markdown", filename=f"summary_{transcript_id}.md")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
