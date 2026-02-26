#!/usr/bin/env sh

# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
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

# BYOT Bash helper:
#   source scripts/byot_telemetry_sdk.sh
#   byot_emit_internal "tool.scan" "scanner-bot" "urn:target:ip:10.0.0.5" "success" '{"ports":[22,443]}'
#   byot_emit_cloudevent "com.nyxera.scan.v1" "urn:tool:scanner" "task-1" '{"status":"success"}'

byot_emit_internal() {
  event_type="$1"
  actor="$2"
  target="$3"
  status="$4"
  attributes_json="${5:-{}}"

  printf '%s\n' "{\"event_type\":\"${event_type}\",\"actor\":\"${actor}\",\"target\":\"${target}\",\"status\":\"${status}\",\"attributes\":${attributes_json}}"
}

byot_emit_cloudevent() {
  event_type="$1"
  source="$2"
  subject="$3"
  data_json="$4"
  event_id="${5:-byot-$(date +%s)}"
  event_time="${6:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

  printf '%s\n' "{\"id\":\"${event_id}\",\"specversion\":\"1.0\",\"type\":\"${event_type}\",\"source\":\"${source}\",\"subject\":\"${subject}\",\"time\":\"${event_time}\",\"data\":${data_json}}"
}
