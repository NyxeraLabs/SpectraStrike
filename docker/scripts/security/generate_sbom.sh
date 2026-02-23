#!/bin/sh
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
