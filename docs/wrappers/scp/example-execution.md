<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SCP Example Execution

```json
{
  "event_type": "scp_session_completed",
  "actor": "scp-wrapper",
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
printf 'live1\n' > /tmp/scp_live_src.txt
SCP_LIVE_TARGET=localhost SCP_LIVE_SOURCE=/tmp/scp_live_src.txt SCP_LIVE_DEST=/tmp/scp_live_dst.txt PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 --check-scp --check-scp-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... scp_binary_ok=True scp_command_ok=True ... checks=...scp.version,scp.command.live
```

E2E test 2:

```bash
printf 'live2\n' > /tmp/scp_live_src2.txt
SCP_LIVE_TARGET=localhost SCP_LIVE_SOURCE=/tmp/scp_live_src2.txt SCP_LIVE_DEST=/tmp/scp_live_dst2.txt PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 --check-scp --check-scp-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... scp_binary_ok=True scp_command_ok=True ... checks=...scp.version,scp.command.live
```
