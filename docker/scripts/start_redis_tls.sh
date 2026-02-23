#!/bin/sh
set -eu

TLS_SRC="/etc/redis/pki/redis"
TLS_DST="/tmp/redis-tls"

mkdir -p "${TLS_DST}"
cp "${TLS_SRC}/server.crt" "${TLS_DST}/server.crt"
cp "${TLS_SRC}/server.key" "${TLS_DST}/server.key"
cp "/etc/redis/pki/ca.crt" "${TLS_DST}/ca.crt"

chmod 600 "${TLS_DST}/server.key"
chmod 644 "${TLS_DST}/server.crt" "${TLS_DST}/ca.crt"

exec redis-server \
  --appendonly yes \
  --save 900 1 \
  --port 0 \
  --tls-port 6380 \
  --tls-cert-file "${TLS_DST}/server.crt" \
  --tls-key-file "${TLS_DST}/server.key" \
  --tls-ca-cert-file "${TLS_DST}/ca.crt" \
  --tls-auth-clients yes \
  --protected-mode yes
