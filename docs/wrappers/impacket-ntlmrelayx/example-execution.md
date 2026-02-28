<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Impacket ntlmrelayx.py Example Execution

```json
{
  "event_type": "impacket_ntlmrelayx_completed",
  "actor": "impacket_ntlmrelayx-wrapper",
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

Successful ntlmrelayx smoke execution:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-impacket-ntlmrelayx
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... impacket_ntlmrelayx_binary_ok=True impacket_ntlmrelayx_command_ok=True ... checks=...impacket.ntlmrelayx.version,impacket.ntlmrelayx.command
```

Live ntlmrelayx E2E gate (documented blocker):

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-impacket-ntlmrelayx \
  --check-impacket-ntlmrelayx-live
```

```text
HostIntegrationError: IMPACKET_NTLMRELAYX_PASSWORD or IMPACKET_NTLMRELAYX_HASHES is required for live ntlmrelayx e2e
```
