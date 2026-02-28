<!-- NYXERA_BRANDING_HEADER_START -->
<p align="center">
  <img src="https://spectrastrike.nyxera.cloud/branding/spectrastrike-logo.png" alt="SpectraStrike" width="220" />
</p>

<p align="center">
  <a href="https://docs.spectrastrike.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_HEADER_END -->

<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
-->

# Security Policy – SpectraStrike
![SpectraStrike Logo](ui/web/assets/images/SprectraStrike_Logo.png)


**Author:** José María Micoli  
**Intellectual Property Holder:** Nyxera Labs  
**License:** Business Source License 1.1 (BSL 1.1)

---

## 1. Overview

SpectraStrike is a professional offensive security orchestration platform.  
Security of our software, infrastructure, and customer data is our top priority.  
This document outlines responsible disclosure, reporting procedures, and security best practices.

Governance companion policy:
- `docs/SECURITY_POLICY.md`

---

## 2. Reporting a Vulnerability

We encourage responsible disclosure from researchers, clients, and partners:

1. **Identify:** Collect detailed information about the vulnerability.  
2. **Report:** Email **security@nyxera.cloud** with:
   - Description and impact
   - Steps to reproduce
   - Affected versions
3. **Do Not Publicly Disclose** until resolved.

We respond promptly and may recognize contributions or provide rewards at our discretion.

Required reporting channel:
- `security@nyxera.cloud`

---

## 3. Supported Versions

- Only actively maintained versions of SpectraStrike are supported.  
- Security patches are applied to the latest stable release.  
- Deprecated versions may not receive security fixes.

---

## 4. Security Updates & Patching

- Dependencies are monitored for CVEs.  
- Critical vulnerabilities patched within **48 hours**.  
- Minor updates are scheduled in regular releases.

---

## 5. Secure Development Practices

SpectraStrike follows industry best practices:

- Input validation and sanitization
- Authentication/Authorization/Auditing (AAA)
- TLS/SSL encryption for communications
- Audit logging and telemetry for all critical operations
- Module/container isolation
- CI/CD pipelines with pre-commit hooks
- Unit and integration testing for all modules

---

## 6. Client Responsibilities

Clients are responsible for:

- Secure deployment environments
- Protecting credentials and API keys
- Monitoring telemetry and logs
- Applying updates promptly

---

## 7. Contact

- **Email:** security@nyxera.cloud  
- **Response Time:** Within 24 hours for critical issues  

---

*SpectraStrike is licensed under BSL 1.1; commercial use and redistribution are controlled per license terms.*

<!-- NYXERA_BRANDING_FOOTER_START -->

---

<p align="center">
  <img src="https://spectrastrike.nyxera.cloud/branding/nyxera-logo.png" alt="Nyxera Labs" width="110" />
</p>

<p align="center">
  2026 SpectraStrike by Nyxera Labs. All rights reserved.
</p>

<p align="center">
  <a href="https://docs.spectrastrike.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_FOOTER_END -->
