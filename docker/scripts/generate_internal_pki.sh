#!/bin/sh
set -eu

PKI_DIR="docker/pki"
mkdir -p "${PKI_DIR}/rabbitmq" "${PKI_DIR}/app" "${PKI_DIR}/postgres" "${PKI_DIR}/redis"

new_ext_file() {
  ext_path="$1"
  usage="$2"
  san="$3"
  cat > "${ext_path}" <<EOF
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=${usage}
subjectAltName=${san}
EOF
}

issue_cert() {
  cn="$1"
  key_path="$2"
  csr_path="$3"
  crt_path="$4"
  usage="$5"
  san="$6"
  ext_path="$7"

  openssl genrsa -out "${key_path}" 4096
  openssl req -new -key "${key_path}" -out "${csr_path}" -subj "/C=US/O=SpectraStrike/CN=${cn}"
  new_ext_file "${ext_path}" "${usage}" "${san}"
  openssl x509 -req -in "${csr_path}" \
    -CA "${PKI_DIR}/ca.crt" -CAkey "${PKI_DIR}/ca.key" -CAcreateserial \
    -out "${crt_path}" -days 365 -sha256 -extfile "${ext_path}"
}

# Root CA
openssl genrsa -out "${PKI_DIR}/ca.key" 4096
openssl req -x509 -new -nodes -key "${PKI_DIR}/ca.key" -sha256 -days 365 \
  -out "${PKI_DIR}/ca.crt" -subj "/C=US/O=SpectraStrike/CN=SpectraStrike-Local-CA"

# Service/server certificates
issue_cert "rabbitmq" "${PKI_DIR}/rabbitmq/server.key" "${PKI_DIR}/rabbitmq/server.csr" \
  "${PKI_DIR}/rabbitmq/server.crt" "serverAuth" "DNS:rabbitmq" "${PKI_DIR}/rabbitmq/server.ext"
issue_cert "postgres" "${PKI_DIR}/postgres/server.key" "${PKI_DIR}/postgres/server.csr" \
  "${PKI_DIR}/postgres/server.crt" "serverAuth" "DNS:postgres" "${PKI_DIR}/postgres/server.ext"
issue_cert "redis" "${PKI_DIR}/redis/server.key" "${PKI_DIR}/redis/server.csr" \
  "${PKI_DIR}/redis/server.crt" "serverAuth" "DNS:redis" "${PKI_DIR}/redis/server.ext"

# Shared app client certificate for internal mTLS calls
issue_cert "app-client" "${PKI_DIR}/app/client.key" "${PKI_DIR}/app/client.csr" \
  "${PKI_DIR}/app/client.crt" "clientAuth" "DNS:app" "${PKI_DIR}/app/client.ext"

chmod 600 \
  "${PKI_DIR}/ca.key" \
  "${PKI_DIR}/rabbitmq/server.key" \
  "${PKI_DIR}/postgres/server.key" \
  "${PKI_DIR}/redis/server.key" \
  "${PKI_DIR}/app/client.key"

echo "Internal PKI generated under ${PKI_DIR}"
