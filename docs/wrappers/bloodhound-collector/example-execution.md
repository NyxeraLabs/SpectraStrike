<!-- NYXERA_BRANDING_HEADER_START -->
<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/product-logo.png" alt="SpectraStrike" width="220" />
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_HEADER_END -->

<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# BloodHound Collector Example Execution

```json
{
  "event_type": "bloodhound_collector_completed",
  "actor": "bloodhound_collector-wrapper",
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

Successful BloodHound collector smoke execution:

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-bloodhound-collector
```

```text
HOST_SMOKE tenant_id=10000000-0000-0000-0000-000000000001 ... bloodhound_collector_binary_ok=True bloodhound_collector_command_ok=True ... checks=...bloodhound.collector.version,bloodhound.collector.command
```

Live BloodHound collector E2E gate (documented blocker):

```bash
PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python \
  -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --timeout-seconds 30 \
  --check-bloodhound-collector \
  --check-bloodhound-collector-live
```

```text
HostIntegrationError: BLOODHOUND_COLLECTOR_PASSWORD is required for live bloodhound collector e2e
```

<!-- NYXERA_BRANDING_FOOTER_START -->

---

<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/nyxera-logo.png" alt="Nyxera Labs" width="110" />
</p>

<p align="center">
  2026 SpectraStrike by Nyxera Labs. All rights reserved.
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_FOOTER_END -->
