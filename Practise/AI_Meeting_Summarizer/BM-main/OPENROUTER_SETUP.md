# OpenRouter setup

The app now uses OpenRouter for summaries and action-item extraction. Keep the
API key out of source code and set it in the shell that starts FastAPI:

```powershell
$env:OPENROUTER_API_KEY = "your_openrouter_key"
# Optional: choose any chat model available to your OpenRouter account.
$env:OPENROUTER_MODEL = "openai/gpt-4o-mini"
uvicorn app:app --reload
```

When using shell variables, set the key again before starting the API in a new
terminal. The project also automatically loads `.env`, which is ignored by Git.

Audio recordings are transcribed through OpenRouter too. By default the app
uses `openai/whisper-large-v3`; optionally configure a different supported STT
model with `OPENROUTER_TRANSCRIPTION_MODEL`.

If the key is missing or OpenRouter is unavailable, `/summarize` and
`/extract_actions` return a clear HTTP 503 error.
