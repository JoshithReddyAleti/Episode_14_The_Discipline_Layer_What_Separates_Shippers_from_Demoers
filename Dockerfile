# Reference Dockerfile for Episode 14 utilities and examples.
FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY src/ ./src/
COPY examples/ ./examples/
COPY tests/ ./tests/

ENV PYTHONPATH=/app/src

CMD ["python", "-c", "print('Episode 14 container ready. Explore src/, examples/, or run pytest tests/.')"]
