<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Responder Signature Verification

Signature controls:
- Signing algorithm is restricted to Ed25519.
- Canonical payload serialization is required before signing.
- Validation must fail closed on signature mismatch.
- Symmetric-signing fallback is not allowed.
