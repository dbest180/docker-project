# ─────────────────────────────────────────────
#  STAGE 1: builder
#  Create a venv and install all dependencies
#  in isolation. Nothing here bleeds into the
#  final image except the /venv directory.
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy only requirements first — Docker caches this layer
# separately so rebuilds are fast when code changes but
# requirements haven't.
COPY app/requirements.txt .

# Using a venv is the reliable cross-platform way to isolate
# packages for copying into the next stage (avoids --prefix quirks).
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────
#  STAGE 2: runtime
#  Lean final image — no build tools, no cache.
# ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Pull in the fully-installed venv from builder
COPY --from=builder /venv /venv

# Copy application code
COPY app/ .

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

USER appuser

# Make the venv's binaries the default Python/uvicorn
ENV PATH="/venv/bin:$PATH"

EXPOSE 8000

# Healthcheck so Docker (and Compose) knows when the app is ready
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]