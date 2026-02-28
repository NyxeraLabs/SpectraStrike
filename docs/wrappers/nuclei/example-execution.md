<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Nuclei Example Execution

```json
{
  "event_type": "nuclei_scan_completed",
  "actor": "nuclei-wrapper",
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

Successful nuclei smoke execution:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-nuclei
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... nuclei_binary_ok=True nuclei_command_ok=True ... checks=...nuclei.version,nuclei.command
```

Live nuclei E2E gate (documented blocker):

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-nuclei \
  --check-nuclei-live
```

```text
HostIntegrationError: NUCLEI_LIVE_TARGET is required for live nuclei e2e
```
