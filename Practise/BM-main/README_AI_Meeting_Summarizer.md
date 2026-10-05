AI Meeting Summarizer & Action-Item Tracker
===========================================

Overview
--------
This project is a Python-based prototype for the "AI Meeting Summarizer & Action-Item Tracker" described in the provided spec. It provides:

- Transcript ingestion (plain text).
- Speech-to-text transcription of recorded or uploaded meetings (local Whisper model).
- A summarization endpoint producing a concise meeting summary.
- Action-item extraction returning structured data (task, owner, deadline).
- Storage of transcripts, summaries and action items on disk (JSON files) with a lightweight retrieval interface for follow-up Q&A.
- A tracker to maintain action-item status (open/done) across meetings.
- Export endpoint for summaries and action items as markdown.

This scaffold is intentionally minimal and uses heuristic/local implementations so it can run without external LLMs or paid APIs. Hooks are provided where an LLM or embedding model can be integrated for production use.

Files
-----
- app.py — FastAPI backend exposing endpoints for ingest, summarize, extract, query, track, export.
- streamlit_app.py — Streamlit web interface for the backend.
- ingest.py — transcript ingestion helpers.
- summarizer.py — simple summarization heuristics; replace with LLM call as needed.
- extractor.py — heuristics to extract action items (task, owner, deadline).
- store.py — simple file-based store for transcripts, summaries, and action items.
- tracker.py — action-item tracking utilities (status updates, list status view).
- sample_transcript.txt — example meeting transcript to try the API.
- requirements.txt — recommended packages to install when moving to an advanced setup.

Mapping to Functional Requirements
----------------------------------
1) Transcript ingestion (plain text) — ingest.py + app.py /ingest
2) Summarization pipeline — summarizer.py + app.py /summarize
3) Action-item extraction returning structured data — extractor.py + app.py /extract_actions
4) Vector store of past meeting transcripts — store.py contains a placeholder vector API and persistence; replace with an embedding-backed vector store later.
5) Action-item tracker view showing status — tracker.py + app.py /track
6) Export option for summaries and action items — app.py /export

How to run (development)
------------------------
1) (Optional) Create a virtualenv and activate it.
2) pip install -r requirements.txt (only necessary if using the optional libraries)
3) Start the API: `uvicorn app:app --reload`
4) In a second terminal, start the UI: `streamlit run streamlit_app.py`

The API runs on http://127.0.0.1:8000 and its interactive documentation is at
http://127.0.0.1:8000/docs. The Streamlit UI opens at http://localhost:8501.

Speech-to-text is powered by a local Whisper model. The selected model downloads the
first time you transcribe a recording; use `tiny` for the fastest first test.

Notes for production
--------------------
- Replace summarizer.summarize_text with a call to an LLM (OpenAI, local LLM) for higher-quality summaries.
- Replace store.py vector placeholders with a real embedding + vector DB (FAISS, Milvus, Pinecone) for RAG.
- Add authentication for API endpoints if exposing externally.

Evaluation alignment
--------------------
The project includes evaluation hooks in summarizer.py and extractor.py so a subject-matter expert can test: summary quality, action-item extraction, follow-up Q&A relevance, tracking usability, and code quality.

License & authorship
--------------------
Scaffold created by: Copilot CLI runtime in VS Code (assistant). Update as needed.
