# SpectraStrike – Security Policy

Nyxera Labs is committed to maintaining the security and integrity of SpectraStrike.

## Supported Versions

| Version | Supported |
|---------|------------|
| 1.x     | ✅ Yes     |
| <1.0    | ❌ No      |

## Reporting a Vulnerability

If you discover a security vulnerability:

1. DO NOT create a public issue.
2. Send a detailed report to:
   security@nyxeralabs.com
3. Include:
   - Description
   - Steps to reproduce
   - Impact assessment
   - Suggested remediation (if known)

We aim to respond within 72 hours.

## Responsible Disclosure

Nyxera Labs follows responsible disclosure practices:

- Confidential triage
- Coordinated remediation
- Credit to reporters (if desired)
- Public advisory when appropriate

## Security Design Principles

SpectraStrike is built with:

- Strong typing and input validation
- Structured logging
- Minimal privilege design
- API boundary isolation
- Export-safe structured outputs (VectorVue-ready)
- Separation between detection and execution layers

## Security Model

SpectraStrike assumes:

- Deployment in controlled infrastructure
- Hardened host environment
- Network-level segmentation
- Proper IAM configuration

SpectraStrike does NOT replace:
- SIEM hardening
- Endpoint security
- Access control policies

It is a detection & orchestration engine — not a perimeter defense tool.