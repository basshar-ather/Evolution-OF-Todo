FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# copy only requirements first for better caching
COPY ../../phase-1/backend/requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy application
COPY ../../phase-1/backend /app

ENV DATABASE_URL="sqlite:////data/database.db"

RUN mkdir -p /data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Placeholder Dockerfile for Phase IV
