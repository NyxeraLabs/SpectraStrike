#!/bin/sh
set -eu

FILES="docker-compose.dev.yml docker-compose.prod.yml"

for f in ${FILES}; do
  if rg -n "image: .*:latest" "${f}" >/dev/null; then
    echo "policy violation: latest tag in ${f}" >&2
    exit 1
  fi

  if rg -n "privileged:\s*true" "${f}" >/dev/null; then
    echo "policy violation: privileged mode in ${f}" >&2
    exit 1
  fi

  if ! rg -n "no-new-privileges:true" "${f}" >/dev/null; then
    echo "policy violation: no-new-privileges missing in ${f}" >&2
    exit 1
  fi

done

echo "compose policy checks passed"
