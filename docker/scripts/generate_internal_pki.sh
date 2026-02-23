#!/bin/sh
set -eu

PKI_DIR="docker/pki"
mkdir -p "${PKI_DIR}/rabbitmq" "${PKI_DIR}/app"

# Root CA
openssl genrsa -out "${PKI_DIR}/ca.key" 4096
openssl req -x509 -new -nodes -key "${PKI_DIR}/ca.key" -sha256 -days 365 \
  -out "${PKI_DIR}/ca.crt" -subj "/C=US/O=SpectraStrike/CN=SpectraStrike-Local-CA"

# RabbitMQ server cert
openssl genrsa -out "${PKI_DIR}/rabbitmq/server.key" 4096
openssl req -new -key "${PKI_DIR}/rabbitmq/server.key" \
  -out "${PKI_DIR}/rabbitmq/server.csr" -subj "/C=US/O=SpectraStrike/CN=rabbitmq"
openssl x509 -req -in "${PKI_DIR}/rabbitmq/server.csr" \
  -CA "${PKI_DIR}/ca.crt" -CAkey "${PKI_DIR}/ca.key" -CAcreateserial \
  -out "${PKI_DIR}/rabbitmq/server.crt" -days 365 -sha256

# App client cert
openssl genrsa -out "${PKI_DIR}/app/client.key" 4096
openssl req -new -key "${PKI_DIR}/app/client.key" \
  -out "${PKI_DIR}/app/client.csr" -subj "/C=US/O=SpectraStrike/CN=app-client"
openssl x509 -req -in "${PKI_DIR}/app/client.csr" \
  -CA "${PKI_DIR}/ca.crt" -CAkey "${PKI_DIR}/ca.key" -CAcreateserial \
  -out "${PKI_DIR}/app/client.crt" -days 365 -sha256

chmod 600 "${PKI_DIR}/ca.key" "${PKI_DIR}/rabbitmq/server.key" "${PKI_DIR}/app/client.key"

echo "Internal PKI generated under ${PKI_DIR}"
