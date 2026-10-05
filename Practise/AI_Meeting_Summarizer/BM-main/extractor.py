"""LLM-powered action-item extraction via OpenRouter."""
from typing import Dict, List

import llm


def extract_actions(text: str) -> List[Dict]:
    """Return only explicit action items with their stated owner and deadline."""
    if not text.strip():
        return []
    result = llm.chat_json([
        {"role": "system", "content": (
            "Extract only explicit meeting action items. Return a JSON object with an "
            "'actions' array. Each item must have exactly these keys: task (string), "
            "owner (string or null), deadline (string or null), source (the supporting "
            "transcript excerpt). Do not infer missing owners or deadlines."
        )},
        {"role": "user", "content": text},
    ])
    actions = result.get("actions", [])
    if not isinstance(actions, list):
        raise RuntimeError("OpenRouter returned an invalid action-items format.")
    return [
        {
            "task": str(item.get("task", "")).strip(),
            "owner": item.get("owner") or None,
            "deadline": item.get("deadline") or None,
            "source": str(item.get("source", "")).strip(),
        }
        for item in actions
        if isinstance(item, dict) and str(item.get("task", "")).strip()
    ]
