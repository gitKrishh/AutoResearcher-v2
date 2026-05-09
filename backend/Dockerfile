# ============================================
# AutoResearcher Backend — Dockerfile
# ============================================
# Multi-stage build for smaller production image.
# Only production dependencies are installed.
# ============================================

# --- Stage 1: Build ---
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system deps needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- Stage 2: Runtime ---
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create non-root user for security
RUN useradd --create-home appuser

# Create directories for data (FAISS index, PDF cache)
RUN mkdir -p /app/vector_store /app/data/pdfs && \
    chown -R appuser:appuser /app

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Start the server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
