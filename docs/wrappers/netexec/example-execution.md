<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# NetExec Example Execution

```json
{
  "event_type": "netexec_session_completed",
  "actor": "netexec-wrapper",
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
  --check-netexec
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... netexec_binary_ok=True netexec_command_ok=True ... checks=...netexec.version,netexec.command
```

Smoke test 2:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-netexec \
  --check-netexec-live
```

```text
HostIntegrationError: NETEXEC_LIVE_TARGET, NETEXEC_LIVE_USERNAME, and NETEXEC_LIVE_PASSWORD are required for live netexec e2e
```
