<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Impacket wmiexec.py Example Execution

```json
{
  "event_type": "impacket_wmiexec_completed",
  "actor": "impacket_wmiexec-wrapper",
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

Successful wmiexec smoke execution:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-impacket-wmiexec
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... impacket_wmiexec_binary_ok=True impacket_wmiexec_command_ok=True ... checks=...impacket.wmiexec.version,impacket.wmiexec.command
```

Live wmiexec E2E gate (documented blocker):

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-impacket-wmiexec \
  --check-impacket-wmiexec-live
```

```text
HostIntegrationError: IMPACKET_WMIEXEC_PASSWORD or IMPACKET_WMIEXEC_HASHES is required for live wmiexec e2e
```
