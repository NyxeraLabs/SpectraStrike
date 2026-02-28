<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# BurpSuite Telemetry Schema

Primary event type target: burpsuite_scan_completed.

Canonical telemetry fields:
- event_type
- actor
- target
- status
- tenant_id
- attributes.execution_fingerprint
- attributes.attestation_measurement_hash
- attributes.payload_signature
- attributes.payload_signature_algorithm (must be Ed25519)
