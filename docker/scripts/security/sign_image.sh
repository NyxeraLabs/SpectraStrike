#!/bin/sh
set -eu

IMAGE_TAG="${1:-spectrastrike/app:latest}"
KEY_DIR="${2:-docker/secrets/cosign}"
mkdir -p "${KEY_DIR}"

if [ ! -f "${KEY_DIR}/cosign.key" ] || [ ! -f "${KEY_DIR}/cosign.pub" ]; then
  docker run --rm -i \
    -e COSIGN_PASSWORD="${COSIGN_PASSWORD:-}" \
    -v "$(pwd)/${KEY_DIR}":/keys \
    gcr.io/projectsigstore/cosign:v2.4.1 \
    generate-key-pair --output-key-prefix /keys/cosign
fi

docker run --rm -i \
  -e COSIGN_PASSWORD="${COSIGN_PASSWORD:-}" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd)/${KEY_DIR}":/keys \
  gcr.io/projectsigstore/cosign:v2.4.1 \
  sign --yes --key /keys/cosign.key "${IMAGE_TAG}"

echo "image signed: ${IMAGE_TAG}"
