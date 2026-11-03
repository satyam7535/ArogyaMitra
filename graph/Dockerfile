FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel urllib3 && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m pip uninstall -y pip && \
    rm -rf /usr/local/lib/python3.11/ensurepip

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

ENV PORT=8001
EXPOSE 8001

CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}"]
