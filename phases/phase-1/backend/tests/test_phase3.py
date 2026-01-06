import os
import tempfile
import subprocess
import time
import requests
import signal


def start_server_with_db(port="8003"):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite:///{path}"
    env = os.environ.copy()
    env["DATABASE_URL"] = db_url

    import sys
    python_exec = sys.executable
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


def test_chat_add_list_update_delete():
    proc, base, db_path = start_server_with_db()
    try:
        # create user to get token
        r = requests.post(f"{base}/users", json={"username": "bob"}, timeout=2)
        assert r.status_code == 201
        token = r.json()["token"]
        headers = {"Authorization": f"Token {token}"}

        # Add todo via chat
        r = requests.post(f"{base}/chat", json={"message": "Add todo Buy AI milk"}, headers=headers, timeout=2)
        assert r.status_code == 200
        out = r.json()
        assert out.get("result") == "created"
        todo = out.get("todo")
        tid = todo.get("id")

        # List via chat
        r = requests.post(f"{base}/chat", json={"message": "List todos"}, headers=headers, timeout=2)
        assert r.status_code == 200
        out = r.json()
        assert out.get("result") == "list"
        assert any(t.get("id") == tid for t in out.get("todos", []))

        # Update via chat
        r = requests.post(f"{base}/chat", json={"message": f"Update todo {tid} title Buy bread"}, headers=headers, timeout=2)
        assert r.status_code == 200
        out = r.json()
        assert out.get("result") == "updated"
        assert out.get("todo")["title"] == "Buy bread"

        # Delete via chat
        r = requests.post(f"{base}/chat", json={"message": f"Delete todo {tid}"}, headers=headers, timeout=2)
        assert r.status_code == 200
        out = r.json()
        assert out.get("result") == "deleted"

    finally:
        stop_server(proc)
        try:
            os.remove(db_path)
        except Exception:
            pass
