<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# dnsx Telemetry Schema

Primary event type target: dnsx_scan_completed.

Canonical telemetry fields:
- event_type
- actor
- target
- status
- tenant_id
- attributes.adapter (dnsx)
- attributes.module (recon)
- attributes.execution_fingerprint
- attributes.attestation_measurement_hash
- attributes.payload_signature
- attributes.payload_signature_algorithm (must be Ed25519)
- attributes.signature_input_hash
- attributes.tool_sha256
