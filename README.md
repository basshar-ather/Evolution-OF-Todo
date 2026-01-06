Evolution of Todo
=================

This repository contains a five-phase Spec-Driven Development project called "Evolution of Todo". 

Phase I is implemented with FastAPI + SQLModel + SQLite. Subsequent phases are scaffolded.

See `phases/phase-1/backend/README.md` for Phase I run and test instructions.

Finalization notes:
- Alembic migration scaffolding added under `phases/phase-1/backend/alembic/` (run `alembic upgrade head` or use the included `scripts/entrypoint.sh` in the image).
- Helm chart template added at `phases/phase-5/helm/` for Kubernetes deployment.
- `docker-compose.yml` provided for local Postgres + backend testing.
- Use `scripts/build_and_test.ps1` to build and smoke-test the Docker image locally.

