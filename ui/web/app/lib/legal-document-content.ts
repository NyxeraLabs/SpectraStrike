/*
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
*/

export type LegalDocumentId =
  | "license"
  | "eula"
  | "aup"
  | "privacy"
  | "security";

export const legalDocuments: Array<{
  id: LegalDocumentId;
  title: string;
  version: string;
  requiredForRegistration: boolean;
  requiredForLegalAcceptance: boolean;
  confirmLabel: string;
  content: string;
}> = [
  {
    id: "license",
    title: "Business Source License 1.1",
    version: "2026.1",
    requiredForRegistration: true,
    requiredForLegalAcceptance: false,
    confirmLabel: "I have read and accept the Business Source License terms.",
    content: `Business Source License 1.1

Copyright (c) 2026 NyxeraLabs

Author: José María Micoli

Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

Business Source License 1.1

License text copyright © 2017 MariaDB Corporation Ab, All Rights Reserved.
"Business Source License" is a trademark of MariaDB Corporation Ab.

Terms

The Licensor hereby grants you the right to copy, modify, create derivative
works, redistribute, and make non-production use of the Licensed Work. The
Licensor may make an Additional Use Grant, above, permitting limited
production use.

Effective on the Change Date, or the fourth anniversary of the first publicly
available distribution of a specific version of the Licensed Work under this
License, whichever comes first, the Licensor hereby grants you rights under
the terms of the Change License, and the rights granted in the paragraph
above terminate.

If your use of the Licensed Work does not comply with the requirements
currently in effect as described in this License, you must purchase a
commercial license from the Licensor, its affiliated entities, or authorized
resellers, or you must refrain from using the Licensed Work.

All copies of the original and modified Licensed Work, and derivative works
of the Licensed Work, are subject to this License. This License applies
separately for each version of the Licensed Work and the Change Date may vary
for each version of the Licensed Work released by Licensor.

You must conspicuously display this License on each original or modified copy
of the Licensed Work. If you receive the Licensed Work in original or
modified form from a third party, the terms and conditions set forth in this
License apply to your use of that work.

Any use of the Licensed Work in violation of this License will automatically
terminate your rights under this License for the current and all other
versions of the Licensed Work.

This License does not grant you any right in any trademark or logo of
Licensor or its affiliates (provided that you may use a trademark or logo of
Licensor as expressly required by this License).

TO THE EXTENT PERMITTED BY APPLICABLE LAW, THE LICENSED WORK IS PROVIDED ON
AN “AS IS” BASIS. LICENSOR HEREBY DISCLAIMS ALL WARRANTIES AND CONDITIONS,
EXPRESS OR IMPLIED, INCLUDING (WITHOUT LIMITATION) WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND
TITLE.

MariaDB hereby grants you permission to use this License’s text to license
your works, and to refer to it using the trademark “Business Source License”,
as long as you comply with the Covenants of Licensor below.

Covenants of Licensor

In consideration of the right to use this License’s text and the “Business
Source License” name and trademark, Licensor covenants to MariaDB, and to all
other recipients of the licensed work to be provided by Licensor:

1. To specify as the Change License the GPL Version 2.0 or any later version,
   or a license that is compatible with GPL Version 2.0 or a later version,
   where “compatible” means that software provided under the Change License can
   be included in a program with software provided under GPL Version 2.0 or a
   later version. Licensor may specify additional Change Licenses without
   limitation.

2. To either: (a) specify an additional grant of rights to use that does not
   impose any additional restriction on the right granted in this License, as
   the Additional Use Grant; or (b) insert the text “None”.

3. To specify a Change Date.

4. Not to modify this License in any other way.`,
  },
  {
    id: "eula",
    title: "End User License Agreement (EULA)",
    version: "2026.1",
    requiredForRegistration: true,
    requiredForLegalAcceptance: true,
    confirmLabel: "I have read and accept the EULA.",
    content: `# End-User License Agreement (EULA)
SpectraStrike – Nyxera Labs

Effective Date: 2026

This End-User License Agreement ("Agreement") is a legal agreement between you ("User") and Nyxera Labs ("Company") governing the use of SpectraStrike ("Software").

## 1. License Grant

Subject to compliance with this Agreement, Nyxera Labs grants you:

- A limited
- Non-exclusive
- Non-transferable
- Revocable

license to use SpectraStrike under the Business Source License (BSL 1.1), transitioning to Apache-2.0 in accordance with the project license terms.

## 2. Restrictions

You may NOT:

- Use the Software for unlawful purposes
- Remove license headers
- Circumvent technical safeguards
- Resell the Software without authorization
- Offer it as a competing managed service without agreement

## 3. Ownership

All intellectual property rights remain the property of Nyxera Labs.

The Software contains proprietary detection methodologies, orchestration logic, and risk correlation techniques.

## 4. Compliance Responsibility

User is fully responsible for:

- Obtaining written authorization before adversary simulation
- Ensuring lawful deployment
- Regulatory compliance
- Data protection compliance

Nyxera Labs is not responsible for misuse.

## 5. No Warranty

The Software is provided "AS IS".

No guarantees are made regarding:

- Detection accuracy
- Availability
- Fitness for a specific compliance framework
- Immunity from exploitation

## 6. Limitation of Liability

To the maximum extent permitted by law, Nyxera Labs shall not be liable for:

- Direct damages
- Indirect damages
- Business interruption
- Data loss
- Regulatory penalties

## 7. Termination

Violation of this Agreement results in immediate termination of license rights.

## 8. Governing Law

This Agreement shall be governed by the jurisdiction determined by Nyxera Labs' principal place of operation.

---

By installing or using SpectraStrike, you acknowledge and agree to this Agreement.`,
  },
  {
    id: "aup",
    title: "Acceptable Use Policy (AUP)",
    version: "2026.1",
    requiredForRegistration: true,
    requiredForLegalAcceptance: true,
    confirmLabel: "I have read and accept the Acceptable Use Policy.",
    content: `# SpectraStrike Acceptable Use Policy

## 1. Authorized Use Requirement

SpectraStrike may only be used for systems and environments where the operator has explicit legal authorization.

Operators and organizations must maintain scope documentation for all validation activities.

## 2. Permitted Use Cases

Permitted activities include:
- authorized adversary emulation
- detection engineering validation
- telemetry and correlation research in controlled environments
- incident response simulation and readiness testing
- compliance-oriented security control validation

## 3. Prohibited Use Cases

Prohibited activities include:
- unauthorized system access or exploitation
- attacks against third-party systems without legal authorization
- intentional disruption, data destruction, or exfiltration outside approved scope
- operation of SpectraStrike as an unauthorized commercial hosted competitor
- unlawful surveillance or privacy violations

## 4. Operational Safety Requirements

All validation programs must include:
- written scope and target boundaries
- designated accountable owner
- rollback/stop controls for high-risk tasks
- logging and evidence retention
- incident escalation path for unintended impact

## 5. Data and Privacy Obligations

Customers are responsible for lawful telemetry collection, retention, and access controls under applicable law and contractual obligations.

## 6. Security and Abuse Monitoring

Nyxera Labs reserves rights to investigate reported misuse and take appropriate corrective action under license and applicable law.

## 7. Enforcement

Policy violations may result in:
- suspension or revocation of usage rights
- contractual enforcement actions
- referral to legal or regulatory authorities where required

## 8. Reporting Suspected Misuse

Suspected misuse should be escalated through enterprise security governance channels and, where appropriate, to Nyxera Labs security contact points.`,
  },
  {
    id: "privacy",
    title: "Privacy Policy",
    version: "2026.1",
    requiredForRegistration: true,
    requiredForLegalAcceptance: true,
    confirmLabel: "I have read and accept the Privacy Policy.",
    content: `# SpectraStrike Privacy Policy

Effective date: 2026-02-23

## 1. Policy Scope

This policy describes how data is handled in relation to SpectraStrike deployments.

It applies to:
- self-hosted customer deployments
- enterprise-managed environments
- future managed/SaaS service models (if offered)

## 2. Data Categories

### Identity and Account Data
- operator identity metadata
- role and authorization metadata
- session and authentication events

### Telemetry and Security Data
- task execution records
- scanner/integration outputs
- findings and evidence metadata
- operational logs and audit traces

### Technical Platform Metadata
- API access patterns
- infrastructure/service error logs
- service health and control-plane events

## 3. Processing Purpose

Data is processed to:
- execute authorized security validation workflows
- correlate and score security-relevant telemetry
- provide audit, reporting, and compliance evidence
- maintain platform reliability and abuse prevention

No data is sold for advertising purposes.

## 4. Deployment Responsibility Model

### Self-Hosted Mode
The customer organization is the data controller and retains infrastructure-level custody of platform data unless explicitly configured otherwise.

### Managed/SaaS Mode (Future)
Nyxera Labs may operate as processor/sub-processor under contractual controls and documented security safeguards.

## 5. Security Controls

SpectraStrike supports privacy-aligned security controls, including:
- TLS/mTLS transport protections
- role-based access controls
- auditability for security-relevant actions
- hardened runtime and governance checks

## 6. Retention and Deletion

Retention policies are deployment-configurable.
Customers are responsible for policy configuration and legal compliance in self-hosted mode.

## 7. Data Subject and Regulatory Requests

Requests regarding access, correction, deletion, or restriction should be submitted through customer governance channels or, where applicable, to Nyxera Labs support and privacy contacts.

## 8. International Transfer and Jurisdiction

Where data crosses jurisdictions, transfers must be governed by applicable legal mechanisms and enterprise agreements.

## 9. Policy Updates

This policy may be revised as architecture and service models evolve. Material changes should be recorded with revision date and governance approval.`,
  },
  {
    id: "security",
    title: "Security Policy",
    version: "2026.1",
    requiredForRegistration: true,
    requiredForLegalAcceptance: false,
    confirmLabel: "I have read and accept the Security Policy.",
    content: `# SpectraStrike – Security Policy

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

It is a detection & orchestration engine — not a perimeter defense tool.`,
  },
];
