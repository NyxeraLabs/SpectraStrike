# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0
#
# You may:
# Study
# Modify
# Use for internal security testing
#
# You may NOT:
# Offer as a commercial service
# Sell derived competing products

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

RUN addgroup --system appgroup && adduser --system --ingroup appgroup --home /app appuser

COPY src ./src
COPY tests ./tests
COPY docs ./docs
COPY pyproject.toml README.md SECURITY.md LICENSE ./
RUN chown -R appuser:appgroup /app

USER appuser

CMD ["python", "-m", "pkg.orchestrator.run_simulations", "--test"]
