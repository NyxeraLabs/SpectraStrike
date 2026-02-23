#!/bin/sh
set -eu

BASE_CONF="/etc/rabbitmq/rabbitmq.conf"
GEN_CONF="/tmp/rabbitmq.generated.conf"

BOOT_USER_FILE="${RABBITMQ_BOOT_USER_FILE:-/run/secrets/rabbitmq_user}"
BOOT_PASS_FILE="${RABBITMQ_BOOT_PASS_FILE:-/run/secrets/rabbitmq_password}"
BOOT_USER="${RABBITMQ_DEFAULT_USER:-spectra}"
BOOT_PASS="${RABBITMQ_DEFAULT_PASS:-spectra}"

if [ -f "${BOOT_USER_FILE}" ]; then
  BOOT_USER="$(cat "${BOOT_USER_FILE}")"
fi
if [ -f "${BOOT_PASS_FILE}" ]; then
  BOOT_PASS="$(cat "${BOOT_PASS_FILE}")"
fi

cp "${BASE_CONF}" "${GEN_CONF}"
printf "\ndefault_user = %s\ndefault_pass = %s\n" "${BOOT_USER}" "${BOOT_PASS}" >> "${GEN_CONF}"

exec rabbitmq-server -conf "${GEN_CONF}"
