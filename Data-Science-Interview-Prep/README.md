# Data Science Interview Prep Bot

An adaptive mock-interview application built for the Agentic AI & RAG capstone brief.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. The application creates `interview_prep.db` automatically.

## Enable LLM grading with OpenRouter & LangSmith Observability

Create or configure your `app/.env` file with your API keys:

```ini
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# LangSmith Observability & Evaluation
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=ds-interview-prep
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

Then run the application:
```powershell
python -m uvicorn app.main:app --reload
```
*(Environment variables from `app/.env` and `.env` are automatically loaded on startup).*

OpenRouter is used through its OpenAI-compatible base URL. The LLM receives only the question, reference answer, rubric, and learner answer, and returns a JSON score and feedback. If the provider is unavailable or returns invalid output, grading safely falls back to the local scorer.

---

## LangSmith Observability & Evaluation Suite

The application includes end-to-end integration with **LangSmith** for full production observability, automated evaluations, and safe experimentation:

### 1. Production Tracing & Token/Cost Monitoring
- **`wrap_openai` Client Wrapper**: Automatically records token usage (`prompt_tokens`, `completion_tokens`, `total_tokens`), latency, and OpenRouter LLM costs for each grading call.
- **Hierarchical Trace Trees**: Traces root answer submissions (`submit_candidate_answer`) down into grading, ChromaDB retrieval (`vector_rag_retrieval`), memory lookup (`history_tool_lookup`), and state graph transitions (`transition_graph`).
- **Run Metadata & Tagging**: Every trace is tagged with candidate attributes (`learner_id`, `interview_id`, `track`, `stage`, `difficulty`, `prompt_version`) for targeted filtering and debugging in the LangSmith dashboard.

### 2. Multi-Dimensional Quality Evaluation
The automated evaluation pipeline in `app/langsmith_eval.py` assesses LLM performance against expert-labelled holdout benchmarks across 4 dimensions:
* **`absolute_error`**: Absolute score delta vs expert benchmark.
* **`within_15_agreement`**: Percentage of evaluations within 15 points of expert baseline.
* **`feedback_quality`**: Verifies actionable, constructive guidance ($\ge 25$ characters).
* **`rubric_fidelity`**: Checks logical consistency between score and covered/missing concept breakdowns.

### 3. RAG Retrieval & Grounding Benchmark
* **Dataset (`ds-interview-rag-benchmark`)**: Tests ChromaDB `VectorRAG` semantic question retrieval across ML and Analytics tracks.
* **Evaluator (`metric_rag_topic_precision`)**: Quantifies topic precision and alignment with learner practice requirements.

### 4. Regression Testing & Model Comparison
* Run side-by-side experiments in LangSmith to safely compare candidate models (`gpt-4o-mini`, `claude-3.5-haiku`, etc.) or prompt revisions against the benchmark dataset before production deployment.

### 5. User Feedback Logging
* Capture candidate satisfaction ratings and qualitative notes, attached directly to LangSmith trace runs via `POST /api/feedback`.

---

## Design

### High-Level Architecture
```mermaid
flowchart TD
    %% Define styles
    classDef frontend fill:#e6eee9,stroke:#3d5645,stroke-width:2px,color:#1a201d;
    classDef api fill:#ece9f1,stroke:#6b5b95,stroke-width:2px,color:#1a201d;
    classDef agent fill:#faece6,stroke:#d9806b,stroke-width:2px,color:#1a201d;
    classDef db fill:#f9f9f9,stroke:#5f6b64,stroke-width:2px,color:#1a201d;
    classDef obs fill:#e8f4fd,stroke:#2b6cb0,stroke-width:2px,color:#1a201d;

    %% Nodes
    subgraph Client [Frontend UI]
        UI[Cinematic Precision Dashboard<br>HTML / Vanilla JS]:::frontend
    end

    subgraph Backend [FastAPI Server]
        API[FastAPI Endpoints<br>/api/interviews]:::api
        
        subgraph Orchestration [LangGraph Agent Engine]
            LG_Warmup(Warmup Node):::agent
            LG_Tech(Technical Node):::agent
            LG_Case(Case Study Node):::agent
            LG_Behav(Behavioral Node):::agent
            LG_Report(Report Generation Node):::agent
        end
        
        Evaluator[Grading Engine<br>OpenRouter LLM / Rubric Fallback]:::api
    end

    subgraph Observability [LangSmith Platform]
        LS_Traces[Traces & Token Costs<br>ds-interview-prep]:::obs
        LS_Evals[Grader & RAG Evals<br>Benchmark Datasets]:::obs
    end

    subgraph Data & RAG [Storage Layer]
        SQLite[(SQLite DB<br>interview_prep.db)]:::db
        Chroma[(ChromaDB Vector Store<br>chroma_store/)]:::db
    end

    %% Relationships
    UI -- "Start Interview (POST)" --> API
    UI -- "Submit Answer (POST)" --> API
    UI -- "Submit Feedback (POST)" --> API
    
    API --> LG_Warmup
    LG_Warmup --> LG_Tech
    LG_Tech --> LG_Case
    LG_Case --> LG_Behav
    LG_Behav --> LG_Report
    
    %% RAG flow
    LG_Tech -- "Retrieves dynamic question based on track/weakness" --> Chroma
    LG_Case -- "Retrieves dynamic question based on track/weakness" --> Chroma
    
    %% Evaluation flow
    LG_Tech -- "Sends Answer + Rubric" --> Evaluator
    LG_Case -- "Sends Answer + Rubric" --> Evaluator
    LG_Behav -- "Sends Answer + Rubric" --> Evaluator
    
    %% Observability flow
    Evaluator -- "Traces, Tokens & Latency" --> LS_Traces
    API -- "Logs Feedback & Experiments" --> LS_Traces
    Evaluator -. "Automated Evals" .-> LS_Evals
    Chroma -. "Retrieval Evals" .-> LS_Evals
    
    %% Data Persistence
    LG_Warmup -- "Stores Context" --> SQLite
    Evaluator -- "Stores Score & Feedback" --> SQLite
    LG_Report -- "Fetches Session History" --> SQLite
    API -- "Returns Evaluation & Next Turn" --> UI
```

### Execution Flow (Single Turn)
```mermaid
sequenceDiagram
    actor User
    participant Frontend as UI Dashboard
    participant API as FastAPI
    participant LangGraph as Agent Engine
    participant ChromaDB as Vector Store (RAG)
    participant LLM as Evaluator (OpenAI / OpenRouter)
    participant LangSmith as LangSmith Observability
    participant SQLite as Database

    User->>Frontend: Submits Answer
    Frontend->>API: POST /api/interviews/{id}/answer
    
    API->>LangSmith: Start Trace (submit_candidate_answer)
    API->>LangGraph: Invoke Agent with State
    
    LangGraph->>LLM: Evaluate Answer vs Rubric
    LLM->>LangSmith: Log Tokens, Latency & Completion (wrap_openai)
    LLM-->>LangGraph: JSON (Score, Missing/Covered)
    LangGraph->>SQLite: Persist Response & Score
    
    LangGraph->>LangGraph: Update Running Difficulty & Topic Weakness
    
    LangGraph->>ChromaDB: Retrieve next question (Adaptive)
    ChromaDB->>LangSmith: Trace Vector RAG Retrieval
    ChromaDB-->>LangGraph: Best matching Question + Rubric
    
    LangGraph-->>API: Next Stage State
    API->>LangSmith: End Trace
    API-->>Frontend: Evaluation Results + Next Question
```

- **LangGraph staged agent:** explicit warmup → technical → case study → behavioral → report nodes, with stateful score, memory, difficulty, and transition nodes.
- **RAG:** semantic retrieval searches the curated question bank using the selected track, role goal, level, learner weak topics, and current stage; returned question bundles carry reference answers and rubrics.
- **Vector RAG:** ChromaDB persists embeddings for the full question, reference answer, rubric, stage, and track. A local `all-MiniLM-L6-v2` sentence-transformer retrieves semantically relevant question bundles; TF-IDF remains an offline-safe fallback.
- **Adaptive difficulty:** each scored response updates a running score. Strong performance increases difficulty, while a weaker answer holds or reduces it. Recent weak topics are prioritized; topics already mastered in prior sessions are deprioritized.
- **Evaluation:** an OpenRouter-backed LLM grades against the reference answer and weighted rubric; local weighted concept/reference scoring remains as a resilient fallback.
- **Context memory:** SQLite retains learner topic signals and response history across sessions.

## API

- `POST /api/interviews` — start interview (`learner_id`, `track`, `level`)
- `POST /api/interviews/{id}/answer` — submit an answer
- `GET /api/interviews/{id}/report` — final comprehensive report
- `GET /api/learners/{id}/history` — cross-session memory & performance context
- `POST /api/feedback` — submit candidate satisfaction score and feedback to LangSmith
- `GET /api/evaluation/validate` — expert-labelled benchmark comparison for the active grader
- `GET /api/evaluation/langsmith?type=all|grader|rag|regression` — trigger LangSmith automated evaluations

