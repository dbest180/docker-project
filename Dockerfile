# ─────────────────────────────────────────────
#  STAGE 1: builder
#  Install deps in an isolated layer so the
#  final image doesn't carry build tooling.
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy only requirements first — Docker caches this layer
# separately so rebuilds are fast when code changes but
# requirements haven't.
COPY app/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─────────────────────────────────────────────
#  STAGE 2: runtime
#  Lean final image — no build tools, no cache.
# ─────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Pull in installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ .

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Healthcheck so Docker (and Compose) knows when the app is ready
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]