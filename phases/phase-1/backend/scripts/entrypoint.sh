#!/bin/sh
set -e

# Run migrations (alembic) if available
if [ -f ./alembic.ini ]; then
  echo "Running alembic upgrade head..."
  alembic upgrade head || true
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
