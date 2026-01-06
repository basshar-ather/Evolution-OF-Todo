Phase IV Backend Docker image
=============================

This folder contains the `Dockerfile` used to build the backend image for deployment.

Local build & smoke test
------------------------
A helper script is provided at the repo root to build and run a quick smoke test locally:

PowerShell example (from repo root):

```powershell
# Build image, run health check, then stop container
.
\scripts\build_and_test.ps1 -ImageTag evo-todo-backend:local

# Build and push to registry (example):
.
\scripts\build_and_test.ps1 -ImageTag evo-todo-backend:latest -Registry "ghcr.io/your-org" -Push
```

Notes
-----
- The script mounts `./tmp_data` to `/data` inside the container and sets `DATABASE_URL` to `sqlite:////data/database.db` so SQLite data persists across runs.
- Ensure Docker Desktop or your Docker daemon is running before executing the script.
- For CI builds, see `.github/workflows/docker-build.yml` which builds and pushes to GitHub Container Registry on push.
