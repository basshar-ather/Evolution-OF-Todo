"""Run a smoke test in-process using FastAPI TestClient.

This avoids needing uvicorn and uses the app directly. Run from
the repository root with the workspace venv Python.
"""
import sys
from pathlib import Path
import time

# Ensure the backend package is importable
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "phases" / "phase-1" / "backend"
sys.path.insert(0, str(BACKEND))

from app.main import app
from fastapi.testclient import TestClient


def assert_ok(cond, msg: str):
    if not cond:
        print("FAIL:", msg)
        sys.exit(1)


def main():
    client = TestClient(app)
    # brief wait in case startup tasks take moment
    time.sleep(0.1)

    # Create
    payload = {"title": "Smoke test", "description": "phase-1 smoke"}
    r = client.post("/todos", json=payload)
    assert_ok(r.status_code == 201, f"POST /todos status {r.status_code} {r.text}")
    todo = r.json()
    todo_id = todo.get("id")
    assert_ok(todo_id is not None, "created todo missing id")

    # List
    r = client.get("/todos")
    assert_ok(r.status_code == 200, f"GET /todos failed: {r.status_code}")
    todos = r.json()
    assert_ok(any(t.get("id") == todo_id for t in todos), "created todo not in list")

    # Update
    update = {"title": "Smoke test updated", "description": "updated", "status": "completed"}
    r = client.put(f"/todos/{todo_id}", json=update)
    assert_ok(r.status_code == 200, f"PUT failed: {r.status_code} {r.text}")
    updated = r.json()
    assert_ok(updated.get("title") == "Smoke test updated", "title not updated")
    assert_ok(updated.get("status") == "completed", "status not updated")

    # Delete
    r = client.delete(f"/todos/{todo_id}")
    assert_ok(r.status_code == 204, f"DELETE failed: {r.status_code} {r.text}")

    # Verify deletion
    r = client.get("/todos")
    assert_ok(r.status_code == 200, "GET after delete failed")
    todos = r.json()
    assert_ok(not any(t.get("id") == todo_id for t in todos), "todo still present after delete")

    print("In-process smoke test passed")


if __name__ == "__main__":
    main()
