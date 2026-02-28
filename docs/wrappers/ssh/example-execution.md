<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SSH Example Execution

```json
{
  "event_type": "ssh_session_completed",
  "actor": "ssh-wrapper",
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
SSH_LIVE_TARGET=localhost SSH_COMMAND='-V' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 --check-ssh --check-ssh-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... ssh_binary_ok=True ssh_command_ok=True ... checks=...ssh.version,ssh.command.live
```

E2E test 2:

```bash
SSH_LIVE_TARGET=localhost SSH_COMMAND='-G localhost' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 --check-ssh --check-ssh-live
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... ssh_binary_ok=True ssh_command_ok=True ... checks=...ssh.version,ssh.command.live
```
