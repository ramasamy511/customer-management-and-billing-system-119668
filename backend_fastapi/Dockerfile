# syntax=docker/dockerfile:1
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for running FastAPI and building wheels
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src ./src

ENV PYTHONPATH=/app/src

# If using .env or configure environment variables, ensure those are passed at runtime.

EXPOSE 8000

# Entrypoint for running the FastAPI app via Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
