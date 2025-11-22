# Builder stage - install dependencies
FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

# Update system packages and install build dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies to /app/.venv
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Production stage - slim for compatibility with venv
FROM python:3.13-slim-bookworm

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Use the virtualenv's Python
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Run startup script that respects Azure's PORT env var
CMD ["/app/.venv/bin/python", "start.py"]