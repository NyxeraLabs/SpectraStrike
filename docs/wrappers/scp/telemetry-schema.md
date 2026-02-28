<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SCP Telemetry Schema

Primary event type target: scp_session_completed.

Canonical telemetry fields:
- event_type
- actor
- target
- status
- tenant_id
- attributes.adapter (scp)
- attributes.module (transfer)
- attributes.execution_fingerprint
- attributes.attestation_measurement_hash
- attributes.payload_signature
- attributes.payload_signature_algorithm (must be Ed25519)
- attributes.signature_input_hash
- attributes.tool_sha256
