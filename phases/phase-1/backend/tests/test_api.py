import os
import tempfile
import subprocess
import time
import requests
import signal


def start_server_with_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite:///{path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = db_url

    # Start uvicorn using the current Python executable (the test runner's interpreter)
    import sys
    python_exec = sys.executable
    # Use a non-standard port to avoid collisions
    port = "8001"
    cmd = [python_exec, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", port]
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # wait for server to become available
    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            r = requests.get(f"{base}/todos", timeout=0.5)
            if r.status_code == 200:
                return proc, base, path
        except Exception:
            time.sleep(0.1)
    # if server didn't start, kill process and raise
    proc.kill()
    raise RuntimeError("Server failed to start")


def stop_server(proc):
    try:
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=2)
    except Exception:
        proc.kill()


def test_crud_cycle():
    proc, base, db_path = start_server_with_db()
    try:
        # Create
        r = requests.post(f"{base}/todos", json={"title": "T1", "description": "d1"}, timeout=2)
        assert r.status_code == 201
        todo = r.json()
        todo_id = todo["id"]

        # List
        r = requests.get(f"{base}/todos", timeout=2)
        assert r.status_code == 200
        assert any(t["id"] == todo_id for t in r.json())

        # Update
        r = requests.put(f"{base}/todos/{todo_id}", json={"title": "T1-up", "description": "d2", "status": "completed"}, timeout=2)
        assert r.status_code == 200
        updated = r.json()
        assert updated["title"] == "T1-up"
        assert updated["status"] == "completed"

        # Delete
        r = requests.delete(f"{base}/todos/{todo_id}", timeout=2)
        assert r.status_code == 204

        r = requests.get(f"{base}/todos", timeout=2)
        assert not any(t["id"] == todo_id for t in r.json())
    finally:
        stop_server(proc)
        try:
            os.remove(db_path)
        except Exception:
            pass
