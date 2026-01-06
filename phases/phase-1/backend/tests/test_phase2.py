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

    import sys
    python_exec = sys.executable
    port = "8002"
    cmd = [python_exec, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", port]
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            r = requests.get(f"{base}/todos", timeout=0.5)
            if r.status_code == 200:
                return proc, base, path
        except Exception:
            time.sleep(0.1)
    proc.kill()
    raise RuntimeError("Server failed to start")


def stop_server(proc):
    try:
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=2)
    except Exception:
        proc.kill()


def test_phase2_auth_and_filters():
    proc, base, db_path = start_server_with_db()
    try:
        # create user
        r = requests.post(f"{base}/users", json={"username": "alice"}, timeout=2)
        assert r.status_code == 201
        token = r.json()["token"]
        headers = {"Authorization": f"Token {token}"}

        # create two todos with different due dates and priorities
        r1 = requests.post(f"{base}/todos", json={"title": "A", "description": "a", "priority": 1, "due_date": "2026-01-10T00:00:00"}, headers=headers, timeout=2)
        assert r1.status_code == 201
        id1 = r1.json()["id"]

        r2 = requests.post(f"{base}/todos", json={"title": "B", "description": "b", "priority": 2, "due_date": "2026-01-05T00:00:00"}, headers=headers, timeout=2)
        assert r2.status_code == 201
        id2 = r2.json()["id"]

        # update one to completed
        r = requests.put(f"{base}/todos/{id2}", json={"title": "B", "description": "b", "status": "completed", "priority": 2, "due_date": "2026-01-05T00:00:00"}, headers=headers, timeout=2)
        assert r.status_code == 200

        # filter by completed=true
        r = requests.get(f"{base}/todos?completed=true", headers=headers, timeout=2)
        assert r.status_code == 200
        arr = r.json()
        assert any(t["id"] == id2 for t in arr)

        # sort by due_date ascending
        r = requests.get(f"{base}/todos?sort=due_date", headers=headers, timeout=2)
        assert r.status_code == 200
        arr = r.json()
        # due_date of first should be earlier (2026-01-05)
        assert arr[0]["id"] == id2

    finally:
        stop_server(proc)
        try:
            os.remove(db_path)
        except Exception:
            pass
