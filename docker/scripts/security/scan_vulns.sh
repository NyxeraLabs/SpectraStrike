#!/bin/sh
set -eu

IMAGE_TAG="${1:-spectrastrike/app:latest}"
SEVERITIES="${2:-critical,high}"

# Fail on high/critical findings by default.
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  anchore/grype:v0.84.0 \
  "${IMAGE_TAG}" --fail-on high --only-fixed --by-cve --scope all-layers

echo "vulnerability scan passed for ${IMAGE_TAG}"
