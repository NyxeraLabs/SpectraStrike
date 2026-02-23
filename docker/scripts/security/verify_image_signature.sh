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

IMAGE_TAG="${1:-spectrastrike/app:latest}"
PUB_KEY="${2:-docker/secrets/cosign/cosign.pub}"

if [ ! -f "${PUB_KEY}" ]; then
  echo "missing public key: ${PUB_KEY}" >&2
  exit 1
fi

docker run --rm -i \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd)":/workspace \
  gcr.io/projectsigstore/cosign:v2.4.1 \
  verify --key "/workspace/${PUB_KEY}" "${IMAGE_TAG}"

echo "signature verified: ${IMAGE_TAG}"
