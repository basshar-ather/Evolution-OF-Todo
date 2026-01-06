from typing import Optional, Dict, Any
import os
import requests
from .models import TodoCreate


def _call_llm(prompt: str) -> Optional[str]:
    """Call an OpenAI-compatible endpoint using `AI_API_KEY` env var.
    Returns the model text or None on failure. If no key is present, returns None.
    """
    api_key = os.environ.get("AI_API_KEY")
    if not api_key:
        return None
    url = os.environ.get("AI_API_URL", "https://api.openai.com/v1/chat/completions")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": os.environ.get("AI_MODEL", "gpt-4o-mini"),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 256,
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
        return None
    except Exception:
        return None


def _rule_based_parse(message: str):
    m = message.strip().lower()
    if m.startswith("create todo") or m.startswith("add todo"):
        # support formats: 'create todo: Title | description', 'add todo: Title',
        # and 'add todo Title' (no colon)
        if ":" in message:
            parts = message.split(":", 1)
            if len(parts) == 2:
                title_desc = parts[1].split("|", 1)
                title = title_desc[0].strip()
                desc = title_desc[1].strip() if len(title_desc) > 1 else ""
                return ("create", {"title": title, "description": desc})
        # fallback: 'add todo Title'
        tokens = message.split()
        if len(tokens) >= 3:
            title = " ".join(tokens[2:]).strip()
            return ("create", {"title": title, "description": ""})
    if m.startswith("list todos") or m.startswith("show todos"):
        return ("list", {})
    if m.startswith("delete todo"):
        parts = message.split()
        if len(parts) >= 3:
            return ("delete", {"id": parts[2]})
    if m.startswith("update todo"):
        # support 'update todo <id>: Title | description | status'
        parts = message.split(":", 1)
        if len(parts) == 2:
            left = parts[0].split()
            tid = left[2] if len(left) >= 3 else None
            fields = parts[1].split("|")
            title = fields[0].strip() if len(fields) > 0 else None
            desc = fields[1].strip() if len(fields) > 1 else None
            status = fields[2].strip() if len(fields) > 2 else None
            data = {k: v for k, v in [("title", title), ("description", desc), ("status", status)] if v}
            return ("update", {"id": tid, "data": data})
        # support 'update todo <id> title New title'
        tokens = message.split()
        if len(tokens) >= 5:
            tid = tokens[2]
            field = tokens[3].lower()
            value = " ".join(tokens[4:]).strip()
            if field in ("title", "description", "status"):
                return ("update", {"id": tid, "data": {field: value}})
    return ("unknown", {})


def handle_chat(message: str, user=None) -> Dict[str, Any]:
    """Interpret a user message as a Todo intent. Prefer LLM when `AI_API_KEY` is set,
    otherwise fall back to a deterministic rule-based parser. For safety the LLM
    path is optional and will not be used during tests unless the environment
    variable is provided.
    """
    llm_prompt = f"Interpret this user message as a Todo intent and return a JSON object with intent and payload: {message}"
    llm_resp = _call_llm(llm_prompt)
    if llm_resp:
        try:
            import json

            parsed = json.loads(llm_resp)
            intent = parsed.get("intent")
            payload = parsed.get("payload", {})
        except Exception:
            intent, payload = _rule_based_parse(message)
    else:
        intent, payload = _rule_based_parse(message)

    # If called without a `user` (direct function use in tests), return a
    # simple result dictionary (backwards-compatible). If a `user` is
    # provided, return parsed intent/payload for the endpoint to act on.
    if not user:
        if intent == "create":
            todo_in = TodoCreate(**payload)
            return {"result": "created", "todo": {"title": todo_in.title, "description": todo_in.description}}
        if intent == "list":
            return {"result": "list", "todos": []}
        if intent == "delete":
            return {"result": "delete_requested", "id": payload.get("id")}
        if intent == "update":
            return {"result": "update_requested", "payload": payload}
        return {"result": "unknown"}


def parse_chat(message: str):
    """Convenience wrapper that returns (intent, payload)."""
    out = handle_chat(message)
    # If handle_chat returned a result dict (no user case), convert to intent/payload
    if "intent" in out and "payload" in out:
        return out.get("intent"), out.get("payload")
    # translate result back to intent/payload
    if out.get("result") == "created":
        return "create", {"title": out["todo"]["title"], "description": out["todo"].get("description", "")}
    if out.get("result") == "list":
        return "list", {}
    if out.get("result") == "delete_requested":
        return "delete", {"id": out.get("id")}
    if out.get("result") == "update_requested":
        return "update", out.get("payload", {})
    return "unknown", {}
