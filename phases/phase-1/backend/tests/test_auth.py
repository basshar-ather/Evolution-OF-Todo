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


def test_user_creation_and_auth():
	proc, base, db_path = start_server()
	try:
		# create user
		r = requests.post(f"{base}/users", json={"username": "alice"}, timeout=2)
		assert r.status_code == 201
		token = r.json().get("token")
		assert token

		# create todo with token
		headers = {"Authorization": f"Token {token}"}
		r = requests.post(f"{base}/todos", json={"title": "User todo"}, headers=headers, timeout=2)
		assert r.status_code == 201

		# unauthorized create should fail
		r = requests.post(f"{base}/todos", json={"title": "No auth"}, timeout=2)
		assert r.status_code == 401
	finally:
		stop_server(proc, db_path)

