# ByteMe - AI Meeting Summarizer & Action Tracker

A modern full-stack application for summarizing meeting transcripts and extracting action items. Built with **FastAPI** backend and **Streamlit** frontend.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Download NLTK data** (for sentence tokenization):
```bash
python -c "import nltk; nltk.download('punkt')"
```

### Running the Application

You'll need **two terminal windows** — one for the API backend, one for the frontend.

#### Terminal 1: Start the FastAPI Backend
```bash
uvicorn api_backend:app --reload
```
The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

#### Terminal 2: Start the Streamlit Frontend
```bash
streamlit run streamlit_app.py
```
The UI will open at `http://localhost:8501` (usually auto-opens in your browser)

## 📋 Features

### 1. **Ingest Transcripts** 📥
- Upload or paste meeting transcripts
- Optional metadata: participant name, meeting date
- Auto word-count

### 2. **Summarize** 📊
- Generate concise meeting summaries
- Quality metrics (compression ratio, coverage score)
- Heuristic-based (ready for LLM integration)

### 3. **Extract Action Items** ✅
- Automatically detect tasks, owners, and deadlines
- Parse dates and assign ownership
- Structured action format

### 4. **Track Actions** 🎯
- Capture actions into persistent tracker
- Update status (open → in_progress → done)
- Filter by status

### 5. **Search** 🔍
- Query stored transcripts
- View snippets and metadata
- Load previous transcripts

### 6. **Export** 📥
- Export summary + actions as Markdown
- Ready for sharing or docs

---

## 🏗️ Architecture

### Backend (FastAPI - `api_backend.py`)
- **Modern async framework** with automatic validation
- **Pydantic models** for request/response schemas
- **Auto-generated API docs** at `/docs`
- Endpoints:
  - `POST /ingest` - Store transcript
  - `POST /summarize` - Generate summary
  - `POST /extract_actions` - Extract action items
  - `GET /query` - Search transcripts
  - `POST /track` - Capture actions
  - `POST /track/update` - Update action status
  - `GET /track/list` - List actions
  - `GET /export` - Download as Markdown

### Frontend (Streamlit - `streamlit_app.py`)
- **Interactive web UI** with zero boilerplate
- **Multi-page navigation** (Ingest, Summarize, Extract, Track, Search)
- **Real-time updates** and session state management
- **Responsive design** with custom CSS

### Core Modules
- **`ingest.py`** - Transcript ingestion
- **`summarizer.py`** - Summary generation (heuristics)
- **`extractor.py`** - Action item extraction (heuristics)
- **`tracker.py`** - Action tracking & status management
- **`store.py`** - File-based persistence (JSON)

---

## 🔄 Workflow Example

1. **Open the Streamlit UI** → Ingest Transcript tab
2. **Paste a meeting transcript** (or use the sample)
3. **Click "Ingest Transcript"** → Get transcript ID
4. **Go to Summarize tab** → Click "Generate Summary"
5. **Go to Extract Actions tab** → Click "Extract Action Items"
6. **Go to Track Actions tab** → Click "Capture to Tracker"
7. **Update action statuses** as they're completed
8. **Export** as Markdown

---

## 📊 Sample Transcript

```
Alice: Today we discussed the Q4 roadmap. 
We need to finalize the design by next Friday.
Bob, you're assigned to the design review.

Bob: I'll have the mockups ready by December 15th.

Charlie: I will set up the testing environment by end of month.

Alice: We should also plan the rollout strategy for January.
```

**Generated Summary:**
> Today we discussed Q4 roadmap and upcoming deadlines. Key decisions: finalize design by next Friday, set up testing environment by end of month, plan January rollout strategy.

**Extracted Actions:**
- [ ] Finalize design (Owner: Bob, Due: December 15th)
- [ ] Set up testing environment (Owner: Charlie, Due: end of month)
- [ ] Plan rollout strategy (Owner: Unassigned)

---

## 🛠️ Future Enhancements

### Current Limitations (Heuristic-based):
- **Summarizer:** Simple sentence scoring → Replace with LLM (GPT-4, Mistral, etc.)
- **Extractor:** Regex patterns → Use NER + LLM for better precision
- **Storage:** JSON files → PostgreSQL or MongoDB for scale

### Planned Upgrades:
- [ ] LLM integration (OpenAI, Hugging Face)
- [ ] Vector search (FAISS/Pinecone for semantic search)
- [ ] Database backend (SQLAlchemy + PostgreSQL)
- [ ] Authentication (JWT tokens)
- [ ] Audio/video input (Whisper API)
- [ ] Real-time collaboration
- [ ] Slack/Teams integration
- [ ] Calendar sync for deadlines

---

## 📚 API Documentation

Once the API is running, visit:
```
http://localhost:8000/docs
```
for interactive Swagger UI with all endpoints.

---

## 💡 Why FastAPI + Streamlit?

| Aspect | Flask | FastAPI | Streamlit |
|--------|-------|---------|-----------|
| **Performance** | Sync only | Async-native, 2-3x faster | N/A (UI) |
| **Validation** | Manual | Built-in Pydantic | N/A |
| **API Docs** | Manual setup | Auto-generated | N/A |
| **Development** | More code | Less code | Minimal code |
| **UI** | Need React/Vue | N/A | Zero UI coding |
| **Learning Curve** | Low | Medium | Very low |

**This stack gives you:**
- ✅ Professional REST API (FastAPI)
- ✅ Beautiful interactive UI (Streamlit)
- ✅ Type safety (Pydantic)
- ✅ Async performance (Uvicorn)
- ✅ Rapid development (minimal boilerplate)

---

## 📝 License

MIT

---

## 🙋 Support

For issues or questions:
1. Check API logs in Terminal 1
2. Check Streamlit logs in Terminal 2
3. Ensure `http://localhost:8000` is accessible from the Streamlit app

**Happy summarizing! 🎉**
