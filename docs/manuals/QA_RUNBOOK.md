<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike QA Runbook

## Scope

This runbook defines the minimum enterprise QA/security acceptance workflow for local Dockerized deployments.

## Preconditions

- `.env` configured
- strong secrets set in `docker/secrets/*`
- TLS material generated (`make tls-dev-cert`, `make pki-internal`)

## Command Matrix

1. Configuration and policy gate

```bash
make policy-check
```

2. Unit + integration baseline

```bash
make test
make test-unit
make test-integration
```

3. Containerized execution path

```bash
make test-docker
```

4. Supply-chain and security gate

```bash
make sbom
make vuln-scan
```

5. Combined regression command

```bash
make full-regression
```

## Expected Outcome

- no failing tests
- no compose policy violations
- no high/critical fixed CVEs in image scan
- SBOM artifact generated under `artifacts/sbom`

## Incident Handling

If any gate fails:
- block release/deployment
- record failing command + timestamp
- open remediation task in kanban
- rerun full-regression after fix
