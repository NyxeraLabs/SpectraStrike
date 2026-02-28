<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Subfinder Example Execution

```json
{
  "event_type": "subfinder_scan_completed",
  "actor": "subfinder-wrapper",
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
SUBFINDER_LIVE_TARGET=example.com SUBFINDER_COMMAND='-h' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-subfinder \
  --check-subfinder-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... subfinder_binary_ok=True subfinder_command_ok=True ... checks=...subfinder.version,subfinder.command.live
```

E2E test 2:

```bash
SUBFINDER_LIVE_TARGET=example.com SUBFINDER_COMMAND='--help' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-subfinder \
  --check-subfinder-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... subfinder_binary_ok=True subfinder_command_ok=True ... checks=...subfinder.version,subfinder.command.live
```
