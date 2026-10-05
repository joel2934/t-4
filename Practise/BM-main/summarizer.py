"""LLM-powered meeting transcript summarization via OpenRouter."""
import llm


def summarize_text(text: str, max_sentences: int = 5) -> str:
    """Create a concise, factual meeting summary."""
    if not text.strip():
        return ""
    return llm.chat([
        {"role": "system", "content": (
            "You summarize meeting transcripts accurately. Do not invent facts. "
            "Return concise Markdown with these headings: Overview, Decisions, "
            "and Risks or Open Questions. Use bullets where useful."
        )},
        {"role": "user", "content": text},
    ])


def evaluate_summary(summary: str, transcript: str) -> dict:
    return {"summary_len": len(summary.split()), "transcript_len": len(transcript.split())}
