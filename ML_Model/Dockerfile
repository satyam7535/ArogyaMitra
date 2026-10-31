FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN useradd -m -u 1000 appuser
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel urllib3 && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m pip uninstall -y pip && \
    rm -rf /usr/local/lib/python3.11/ensurepip

# Copy application and model artifacts
COPY app.py __init__.py ./
COPY model/ ./model/
COPY scripts/ ./scripts/
RUN chown -R appuser:appuser /app

USER appuser

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
