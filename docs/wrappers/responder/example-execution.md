<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Responder Example Execution

```json
{
  "event_type": "responder_session_completed",
  "actor": "responder-wrapper",
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

Smoke test 1:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-responder
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... responder_binary_ok=True responder_command_ok=True ... checks=...responder.version,responder.command
```

Smoke test 2:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-responder \
  --check-responder-live
```

```text
HostIntegrationError: RESPONDER_LIVE_INTERFACE is required for live responder e2e
```
