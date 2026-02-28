<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# John the Ripper Example Execution

```json
{
  "event_type": "john_session_completed",
  "actor": "john-wrapper",
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
JOHN_BINARY=/opt/john/run/john PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-john
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... john_binary_ok=True john_command_ok=True ... checks=...john.version,john.command
```

Smoke test 2:

```bash
JOHN_BINARY=/opt/john/run/john JOHN_LIVE_HASH_FILE=/tmp/john_live_hash.txt JOHN_COMMAND='--list=help' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-john \
  --check-john-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... john_binary_ok=True john_command_ok=True ... checks=...john.version,john.command.live
```
