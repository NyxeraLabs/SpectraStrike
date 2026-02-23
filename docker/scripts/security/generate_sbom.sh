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
OUT_DIR="${2:-artifacts/sbom}"
mkdir -p "${OUT_DIR}"

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd)":/workspace \
  anchore/syft:1.10.0 \
  "${IMAGE_TAG}" -o spdx-json="/workspace/${OUT_DIR}/sbom.spdx.json"

echo "sbom generated at ${OUT_DIR}/sbom.spdx.json"
