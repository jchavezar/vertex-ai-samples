# Static comparison site + grade-endpoint (FastAPI on uvicorn).
#
# Security posture:
# - Base: python:3.12-slim — small surface, regular security updates.
# - Runs as non-root user.
# - No env vars baked in. No secrets. No shell-out paths.
# - Only the artifacts listed below are copied in (see .dockerignore).
# - Service runs under a dedicated SA with ZERO IAM bindings.
# - Single POST endpoint (/api/grade) that only logs structured JSON to
#   stdout (Cloud Logging captures it). No DB, no GCS, no Firestore.

FROM python:3.12-slim AS base

# Drop privileges.
RUN groupadd --system app && useradd --system --gid app --home /app app
WORKDIR /app

# Install only the three deps we need.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt \
 && rm -rf /root/.cache

# Copy ONLY the runtime assets (the .dockerignore blocks everything else).
COPY server.py            /app/server.py
COPY race_runner.py       /app/race_runner.py
COPY index.html           /app/index.html
COPY data.json            /app/data.json
COPY sample_50_ids.json   /app/sample_50_ids.json
COPY reference_answers.json /app/reference_answers.json
COPY claude_code_answers.json /app/claude_code_answers.json
COPY validation_sample.json /app/validation_sample.json

USER app

ENV PORT=8080
EXPOSE 8080

# Single worker is plenty for a static site + light POSTs. Tune later if needed.
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080", \
     "--workers", "1", "--access-log", "--no-server-header", "--proxy-headers"]
