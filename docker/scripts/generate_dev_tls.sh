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

CERT_DIR="docker/nginx/certs"
mkdir -p "${CERT_DIR}"

openssl req -x509 -nodes -newkey rsa:4096 \
  -keyout "${CERT_DIR}/tls.key" \
  -out "${CERT_DIR}/tls.crt" \
  -days 365 \
  -subj "/C=US/ST=NA/L=NA/O=SpectraStrike/OU=Dev/CN=localhost"

cp "${CERT_DIR}/tls.crt" "${CERT_DIR}/ca.crt"
chmod 644 "${CERT_DIR}/tls.crt" "${CERT_DIR}/ca.crt" "${CERT_DIR}/tls.key"

echo "generated ${CERT_DIR}/tls.crt, tls.key, ca.crt"
