Phase I - Evolution of Todo - Backend
===================================

Overview
--------
This is the Phase I backend for the Evolution of Todo project. It implements a minimal, spec-driven Todo API using FastAPI and SQLModel with SQLite persistence.

Requirements
------------
- Python 3.9+
- See `requirements.txt` for Python packages

Quick start (Windows)
----------------------
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Start the server:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Endpoints
-------------
- POST /todos          Create a Todo (returns 201)
- GET /todos           List all Todos
- PUT /todos/{id}      Update a Todo
- DELETE /todos/{id}   Delete a Todo (returns 204)

Persistence
-----------
The SQLite database file is created at `phases/phase-1/backend/database.db` and persists across restarts.

Notes
-----
- The implementation follows the Phase I spec exactly and provides only the required behavior and endpoints.

Running the smoke test
----------------------
Ensure the server is running (see Quick start). Then run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/smoke_test.py -q
# or run directly without pytest
python tests/smoke_test.py
```

The smoke test performs a full CRUD sequence against `http://127.0.0.1:8000` by default. Use `TODO_BASE_URL` env var to target a different host.
