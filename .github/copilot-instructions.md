# Copilot / AI Agent Instructions — Evolution of Todo

This file contains concise, project-specific guidance to make AI coding agents productive in this repository.

- **Big picture:** The repo is organized by phased specifications under `phases/`. Phase I contains a runnable backend implemented with FastAPI + SQLModel and SQLite at `phases/phase-1/backend`.
- **Primary components:**
  - **API server:** [phases/phase-1/backend/app/main.py](phases/phase-1/backend/app/main.py) (FastAPI endpoints, startup init)
  - **Persistence:** [phases/phase-1/backend/app/database.py](phases/phase-1/backend/app/database.py) (SQLite by default, `DATABASE_URL` env var overrides)
  - **Data models & CRUD:** [phases/phase-1/backend/app/models.py](phases/phase-1/backend/app/models.py) and [phases/phase-1/backend/app/crud.py](phases/phase-1/backend/app/crud.py)
  - **Auth:** [phases/phase-1/backend/app/auth.py](phases/phase-1/backend/app/auth.py) (expects header `Authorization: Token <token>`; `optional_current_user` returns None when missing)
  - **Chat/AI integration:** [phases/phase-1/backend/app/chat.py](phases/phase-1/backend/app/chat.py) and [phases/phase-1/backend/app/ai_client.py](phases/phase-1/backend/app/ai_client.py) (rule-based parser + optional LLM via `AI_API_KEY`)
  - **Migrations:** `phases/phase-1/backend/alembic/` (alembic scaffolding present)

- **How to run (developer):** see [phases/phase-1/backend/README.md](phases/phase-1/backend/README.md).
  - Create venv, install: `pip install -r phases/phase-1/backend/requirements.txt`.
  - Start dev server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (run from `phases/phase-1/backend`).
  - Smoke tests: run `python tests/smoke_test.py` or `pytest tests/smoke_test.py`. Tests target `http://127.0.0.1:8000` by default; set `TODO_BASE_URL` to override.

- **Key environment variables:**
  - `DATABASE_URL` — override SQLite DB for tests or deployments
  - `AI_API_KEY`, `AI_API_URL`, `AI_MODEL` — enable LLM-based chat parsing in `chat.py`
  - `TODO_BASE_URL` — used by smoke tests

- **Conventions & important patterns (copyable examples):**
  - Auth header format: `Authorization: Token <token>` (see `get_current_user` / `optional_current_user` in auth.py).
  - Use `with get_session() as session:` for DB work (sessions created in `database.py`).
  - UUIDs are primary keys (`models.py` uses `uuid4`) — endpoints accept UUID strings (e.g., `/todos/{todo_id}`).
  - Chat parsing: prefer LLM when `AI_API_KEY` present; otherwise fallback to deterministic rule-based parsing. Example user input handled by rule-parser: `create todo: Buy milk | 2L` → intent `create` with title/description.

- **Developer workflows to know:**
  - Docker / local image + smoke tests: see `docker-compose.yml` and `scripts/build_and_test.ps1` for commands that build the image and exercise the API.
  - Alembic migrations are scaffolded; for local schema apply: `alembic upgrade head` from `phases/phase-1/backend` (or rely on `init_db()` during app startup).

- **When changing API/DB models:**
  - Update `models.py`, `schemas.py` and `crud.py` together. Keep `main.py` response models aligned with `schemas`/`models` types.
  - If persistent DB schema changes are required for Phase I, add an Alembic revision under `alembic/versions` and document migration steps in the relevant phase README.

- **Code style & minimal scope:**
  - Phase I is intentionally minimal and spec-driven — changes should preserve the small, explicit behavior in `phases/phase-1/backend/README.md` unless the user requests Phase II+ work.

- **Quick pointers for an agent making edits:**
  - Prefer edits inside `phases/phase-1/backend/app` for Phase I behaviors. For cross-phase changes, check top-level `phases/*/README.md` first.
  - Run the smoke test locally after API changes: start the server and run `python tests/smoke_test.py` from `phases/phase-1/backend`.
  - For any AI/chat behavior change, preserve the rule-based parser fallback in `chat.py` and gate LLM usage via `AI_API_KEY`.

If anything here is unclear or you'd like additional examples (tests, common refactors, or Docker build commands), tell me which area to expand. I can iterate on this document.
