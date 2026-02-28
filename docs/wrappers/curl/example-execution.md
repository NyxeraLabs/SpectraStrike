<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Curl Example Execution

```json
{
  "event_type": "curl_session_completed",
  "actor": "curl-wrapper",
  "target": "orchestrator",
  "status": "success",
  "tenant_id": "tenant-a",
  "attributes": {
    "execution_fingerprint": "<64-hex>",
    "attestation_measurement_hash": "<64-hex>",
    "payload_signature_algorithm": "Ed25519"
  }
}
```

## Host Integration Smoke Evidence (2026-02-28)

E2E test 1:

```bash
CURL_LIVE_TARGET=http://127.0.0.1 CURL_COMMAND='--version' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 --check-curl --check-curl-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... curl_binary_ok=True curl_command_ok=True ... checks=...curl.version,curl.command.live
```

E2E test 2:

```bash
CURL_LIVE_TARGET=http://127.0.0.1 CURL_COMMAND='--help' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 --check-curl --check-curl-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... curl_binary_ok=True curl_command_ok=True ... checks=...curl.version,curl.command.live
```
