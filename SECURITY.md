# Security Policy – SpectraStrike

**Author:** José María Micoli  
**Intellectual Property Holder:** Nyxera Labs  
**License:** Business Source License 1.1 (BSL 1.1)

---

## 1. Overview

SpectraStrike is a professional offensive security orchestration platform.  
Security of our software, infrastructure, and customer data is our top priority.  
This document outlines responsible disclosure, reporting procedures, and security best practices.

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