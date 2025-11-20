# Builder stage - install dependencies
FROM python:3.14-slim-bookworm AS builder

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

# Production stage - distroless
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

EXPOSE 8000

# Use the virtualenv's Python
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Run uvicorn (without --reload in production)
CMD ["/app/.venv/bin/uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]