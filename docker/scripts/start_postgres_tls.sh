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

TLS_SRC="/etc/postgresql/pki/postgres"
TLS_DST="/var/lib/postgresql/tls"

mkdir -p "${TLS_DST}"
cp "${TLS_SRC}/server.crt" "${TLS_DST}/server.crt"
cp "${TLS_SRC}/server.key" "${TLS_DST}/server.key"
cp "/etc/postgresql/pki/ca.crt" "${TLS_DST}/ca.crt"

chown -R postgres:postgres "${TLS_DST}"
chmod 600 "${TLS_DST}/server.key"
chmod 644 "${TLS_DST}/server.crt" "${TLS_DST}/ca.crt"

exec docker-entrypoint.sh postgres \
  -c ssl=on \
  -c ssl_cert_file="${TLS_DST}/server.crt" \
  -c ssl_key_file="${TLS_DST}/server.key" \
  -c ssl_ca_file="${TLS_DST}/ca.crt" \
  -c hba_file=/etc/postgresql/pg_hba.conf
