import os
from app.chat import handle_chat


def test_rule_based_chat_without_key():
    # Ensure rule-based parsing still works when no AI key is present
    if "AI_API_KEY" in os.environ:
        del os.environ["AI_API_KEY"]
    r = handle_chat("create todo: Buy milk | 2L")
    assert r["result"] == "created"
    assert r["todo"]["title"] == "Buy milk"
