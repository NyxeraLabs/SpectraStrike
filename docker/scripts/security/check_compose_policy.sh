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

  if ! rg -n "start-postgres-tls.sh" "${f}" >/dev/null; then
    echo "policy violation: postgres mTLS startup wrapper missing in ${f}" >&2
    exit 1
  fi

  if ! rg -n "start-redis-tls.sh" "${f}" >/dev/null; then
    echo "policy violation: redis mTLS startup wrapper missing in ${f}" >&2
    exit 1
  fi

  if ! rg -n "POSTGRES_SSL=true" "${f}" >/dev/null; then
    echo "policy violation: postgres TLS client config missing in ${f}" >&2
    exit 1
  fi

  if ! rg -n "REDIS_TLS=true" "${f}" >/dev/null; then
    echo "policy violation: redis TLS client config missing in ${f}" >&2
    exit 1
  fi

done

echo "compose policy checks passed"
