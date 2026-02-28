<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Prowler Example Execution

```json
{
  "event_type": "prowler_scan_completed",
  "actor": "prowler-wrapper",
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

Successful prowler smoke execution:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-prowler
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... prowler_binary_ok=True prowler_command_ok=True ... checks=...prowler.version,prowler.command
```

Live prowler E2E gate (documented blocker):

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-prowler \
  --check-prowler-live
```

```text
HostIntegrationError: PROWLER_LIVE_TARGET is required for live prowler e2e
```
