import os
import tempfile
import subprocess
import time
import requests


def start_server():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite:///{path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = db_url
    import sys
    python_exec = sys.executable
    port = "8003"
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


def stop_server(proc, path):
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        proc.kill()
    try:
        os.remove(path)
    except Exception:
        pass


def test_filtering_and_sorting():
    proc, base, db_path = start_server()
    try:
        # create user
        r = requests.post(f"{base}/users", json={"username": "bob"}, timeout=2)
        assert r.status_code == 201
        token = r.json().get("token")
        headers = {"Authorization": f"Token {token}"}

        # create multiple todos with different due dates and statuses
        r1 = requests.post(f"{base}/todos", json={"title": "A", "due_date": "2026-01-10T00:00:00"}, headers=headers, timeout=2)
        r2 = requests.post(f"{base}/todos", json={"title": "B", "due_date": "2026-01-05T00:00:00", "status": "completed"}, headers=headers, timeout=2)
        r3 = requests.post(f"{base}/todos", json={"title": "C", "due_date": "2026-01-08T00:00:00"}, headers=headers, timeout=2)
        assert r1.status_code == 201 and r2.status_code == 201 and r3.status_code == 201

        # filter completed=true
        r = requests.get(f"{base}/todos?completed=true", headers=headers, timeout=2)
        assert r.status_code == 200
        todos = r.json()
        assert all(t["status"] == "completed" for t in todos)

        # sort by due_date
        r = requests.get(f"{base}/todos?sort=due_date", headers=headers, timeout=2)
        assert r.status_code == 200
        todos = r.json()
        dates = [t.get("due_date") for t in todos if t.get("due_date")]
        assert dates == sorted(dates)
    finally:
        stop_server(proc, db_path)
