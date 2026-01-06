"""Simple smoke test for Phase I Todo API.

Run this while the server is running (default http://127.0.0.1:8000).

Usage:
	python tests/smoke_test.py
"""
import os
import sys
import time
import requests


BASE = os.environ.get("TODO_BASE_URL", "http://127.0.0.1:8000")


def assert_ok(cond, msg: str):
	if not cond:
		print("FAIL:", msg)
		sys.exit(1)


def main():
	print("Smoke test started against:", BASE)
	# Create
	payload = {"title": "Smoke test", "description": "phase-1 smoke"}
	r = requests.post(f"{BASE}/todos", json=payload, timeout=5)
	assert_ok(r.status_code == 201, f"POST /todos status {r.status_code} {r.text}")
	todo = r.json()
	todo_id = todo.get("id")
	assert_ok(todo_id is not None, "created todo missing id")
	print("Created todo id:", todo_id)

	# List
	r = requests.get(f"{BASE}/todos", timeout=5)
	assert_ok(r.status_code == 200, f"GET /todos failed: {r.status_code}")
	todos = r.json()
	assert_ok(any(t.get("id") == todo_id for t in todos), "created todo not in list")
	print("List contains created todo")

	# Update
	update = {"title": "Smoke test updated", "description": "updated", "status": "completed"}
	r = requests.put(f"{BASE}/todos/{todo_id}", json=update, timeout=5)
	assert_ok(r.status_code == 200, f"PUT failed: {r.status_code} {r.text}")
	updated = r.json()
	assert_ok(updated.get("title") == "Smoke test updated", "title not updated")
	assert_ok(updated.get("status") == "completed", "status not updated")
	print("Update succeeded")

	# Delete
	r = requests.delete(f"{BASE}/todos/{todo_id}", timeout=5)
	assert_ok(r.status_code == 204, f"DELETE failed: {r.status_code} {r.text}")
	print("Delete succeeded")

	# Verify deletion
	r = requests.get(f"{BASE}/todos", timeout=5)
	assert_ok(r.status_code == 200, "GET after delete failed")
	todos = r.json()
	assert_ok(not any(t.get("id") == todo_id for t in todos), "todo still present after delete")

	print("Smoke test passed")


if __name__ == "__main__":
	# brief wait in case user just started server
	time.sleep(0.3)
	main()
