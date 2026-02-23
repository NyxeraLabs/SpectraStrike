#!/bin/sh
set -eu

OUT_DIR="${1:-/backup}"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="${OUT_DIR}/postgres_${TS}.sql"
mkdir -p "${OUT_DIR}"

if [ -f /run/secrets/postgres_user ]; then
  DB_USER="$(cat /run/secrets/postgres_user)"
else
  DB_USER="${POSTGRES_USER:-spectra}"
fi

DB_NAME="${POSTGRES_DB:-spectrastrike}"

docker compose -f docker-compose.dev.yml exec -T postgres \
  pg_dump -U "${DB_USER}" "${DB_NAME}" > "${OUT_FILE}"

echo "postgres backup written: ${OUT_FILE}"
