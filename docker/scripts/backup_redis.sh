#!/bin/sh

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


set -eu

OUT_DIR="${1:-/backup}"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="${OUT_DIR}/redis_${TS}.rdb"
mkdir -p "${OUT_DIR}"

docker compose -f docker-compose.dev.yml exec -T redis redis-cli \
  --tls \
  --cacert /etc/redis/pki/ca.crt \
  --cert /etc/redis/pki/app/client.crt \
  --key /etc/redis/pki/app/client.key \
  -p 6380 \
  BGSAVE
sleep 1
docker compose -f docker-compose.dev.yml cp redis:/data/dump.rdb "${OUT_FILE}"

echo "redis backup written: ${OUT_FILE}"
