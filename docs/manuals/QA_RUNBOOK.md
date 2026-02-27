<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike QA Runbook
![SpectraStrike Logo](../../ui/web/assets/images/SprectraStrike_Logo.png)

## 1. Purpose

This runbook defines the enterprise QA governance process for SpectraStrike across application logic, infrastructure hardening, security controls, and documentation integrity.

This runbook is release-gating. Any failed or blocked gate must be recorded in:
- `docs/ROADMAP.md`
- `docs/kanban-board.csv`
- sprint log in `docs/dev-logs/`

## 2. QA Domains

- Platform Core QA: orchestrator, telemetry ingestion, task lifecycle, AAA, audit trail.
- Messaging QA: broker-backed delivery, retries, idempotency, DLQ behavior.
- UI/TUI QA: operator workflows, API wiring, regression behavior.
- Security QA: compose hardening policy, mTLS paths, pinning behavior, supply-chain checks.
- Documentation QA: roadmap/kanban/manual consistency, schema checks, license header compliance.

## 3. Environment Preconditions

- `.env` is configured.
- Secrets are initialized and rotated from placeholders.
- TLS and internal PKI are generated.
- Docker runtime is healthy.
- Python venv is available for local test execution.

Bootstrap sequence:

```bash
cp .env.example .env
make secrets-init
make tls-dev-cert
make pki-internal
make up
```

## 4. Mandatory QA Command Matrix

### 4.1 Policy and configuration gates

```bash
make policy-check
docker compose -f docker-compose.dev.yml config >/dev/null
docker compose -f docker-compose.prod.yml config >/dev/null
```

### 4.2 Python test gates

```bash
make test
make test-unit
make test-integration
make test-docker
```

### 4.3 Security gate

```bash
make security-check
make sbom
make vuln-scan
make security-gate
```

### 4.4 Sprint 9.8 consolidation suite

```bash
./.venv/bin/pytest -q \
  tests/unit/test_telemetry_messaging.py \
  tests/integration/test_messaging_publish_consume.py \
  tests/unit/test_remote_endpoint_config.py \
  tests/unit/integration/test_metasploit_manual_ingestion.py \
  tests/unit/test_ui_admin_client.py \
  tests/unit/test_ui_admin_shell.py \
  tests/qa/test_ui_admin_tui_qa.py \
  tests/unit/test_aaa_framework.py \
  tests/unit/test_orchestrator_audit_trail.py \
  tests/qa/test_orchestrator_qa.py \
  tests/qa/test_docs_qa.py
```

Expected current result: `39 passed`.

### 4.5 Governance and legal enforcement gate

```bash
cat .spectrastrike/legal/acceptance.json
docker compose -f docker-compose.dev.yml exec -T ui-web sh -lc 'cat /var/lib/spectrastrike/legal/acceptance.json'
```

Acceptance file must exist in self-hosted mode and match active versions:
- `eula: 2026.1`
- `aup: 2026.1`
- `privacy: 2026.1` (required for SaaS and enterprise-per-user mode)

Notes:
- local/default non-container path: `.spectrastrike/legal/acceptance.json`
- dockerized runtime path: `/var/lib/spectrastrike/legal/acceptance.json`

If versions differ from `config/legal.config.ts`, access must be blocked with:
- `LEGAL_ACCEPTANCE_REQUIRED`

### 4.6 Sprint 16.7/16.8 host integration smoke

Validate host-installed tooling and integration contracts (tenant-aware telemetry, optional RPC/API live checks).
Sprint 16.8 routes VectorVue validation through RabbitMQ bridge flow.

```bash
export SPECTRASTRIKE_TENANT_ID=tenant-a
make host-integration-smoke

# optional live checks when endpoints/credentials are configured
PYTHONPATH=src .venv/bin/python -m pkg.integration.host_integration_smoke \
  --tenant-id "$SPECTRASTRIKE_TENANT_ID" \
  --check-metasploit-rpc \
  --check-sliver-command \
  --check-mythic-task \
  --check-vectorvue

# optional standalone broker drain -> VectorVue federation gateway sync
make vectorvue-rabbitmq-sync
```

Expected output shape:
- `HOST_SMOKE tenant_id=... nmap_binary_ok=True nmap_scan_ok=True telemetry_ingest_ok=True metasploit_binary_ok=True`
- when Sliver/Mythic checks are enabled:
  - `sliver_binary_ok=True`
  - `sliver_command_ok=True`
  - `mythic_binary_ok=True`
  - `mythic_task_ok=True`
- When `--check-vectorvue` is enabled:
  - `rabbitmq_publish_ok=True`
  - `vectorvue_ok=True`
  - `vectorvue_event_status=accepted|replayed`
  - `vectorvue_finding_status=accepted|replayed`
  - `vectorvue_status_poll_status=accepted|partial|replayed`

If `--check-metasploit-rpc` is enabled, `MSF_RPC_*` must point to a reachable RPC endpoint.
If `--check-vectorvue` is enabled, `VECTORVUE_*` credentials and endpoint must be configured.

Latest local federation evidence (2026-02-27):
- `nmap + metasploit + sliver + vectorvue` host smoke accepted:
  - `vectorvue_event_status=accepted`
  - `vectorvue_finding_status=accepted`
  - `vectorvue_status_poll_status=accepted`
- Mythic-inclusive host smoke currently blocks with:
  - `HostIntegrationError: required binary not found on host: mythic-cli`

### 4.7 Sprint 17 zero-trust QA

Run explicit Sprint 17 denial and containment checks:

```bash
PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_zero_trust_sprint17_qa.py
```

Expected current result: `3 passed`.

### 4.8 Sprint 17 carry-over validation (16.5/16.7/16.8)

Run carry-over regression checks inside Sprint 17 QA gate:

```bash
PYTHONPATH=src .venv/bin/pytest -q \
  tests/unit/test_telemetry_sdk.py \
  tests/unit/test_nmap_wrapper.py \
  tests/unit/test_metasploit_wrapper.py \
  tests/unit/test_host_integration_smoke.py \
  tests/unit/integration/test_vectorvue_rabbitmq_bridge.py
```

Expected current result: `28 passed`.

### 4.9 Sprint 34 microVM transition validation

Run Firecracker transition validation suites:

```bash
PYTHONPATH=src .venv/bin/pytest -q \
  tests/unit/test_firecracker_microvm_runner.py \
  tests/unit/test_universal_edge_runner.py \
  tests/qa/test_sprint34_microvm_transition_qa.py
```

Expected current result: `12 passed`.

## 5. Web UI QA Execution Path

### 5.1 Required dependency bootstrap

```bash
npm --prefix ui/web install --no-audit --no-fund
```

### 5.2 Unit and E2E suites

```bash
npm --prefix ui/web run test:unit
npm --prefix ui/web run test:e2e
```

### 5.3 Current known blocker (Sprint 9.8)

If network DNS cannot resolve npm registry, Web UI QA is blocked and must be recorded exactly.

Observed exact outputs:
- `npm --prefix ui/web install --no-audit --no-fund` -> `EAI_AGAIN getaddrinfo EAI_AGAIN registry.npmjs.org`
- `npm --prefix ui/web run test:unit` -> `sh: line 1: vitest: command not found`
- `npm --prefix ui/web run test:e2e` -> `error: unknown command 'test'`

## 6. mTLS/Transport Verification

Run targeted transport checks inside runtime containers:

```bash
docker compose -f docker-compose.dev.yml exec -T redis redis-cli --tls --cacert /etc/redis/pki/ca.crt --cert /etc/redis/pki/app/client.crt --key /etc/redis/pki/app/client.key -p 6380 ping
docker compose -f docker-compose.dev.yml exec -T postgres psql "host=postgres dbname=spectrastrike user=$(cat docker/secrets/postgres_user.txt) sslmode=verify-ca sslrootcert=/etc/postgresql/pki/ca.crt sslcert=/etc/postgresql/pki/app/client.crt sslkey=/etc/postgresql/pki/app/client.key" -c "select version();"
docker compose -f docker-compose.dev.yml exec -T app python -c "from pkg.orchestrator.messaging import RabbitMQPublisher; print('rabbitmq tls config loaded')"
```

## 7. Documentation QA Gate

Documentation gate is mandatory before release tagging.

```bash
./.venv/bin/python scripts/check_license_headers.py
./.venv/bin/pytest -q tests/qa/test_docs_qa.py
```

The docs QA test enforces:
- manuals index references resolve to existing files
- Sprint 9.5/9.6/9.7 sections in roadmap are complete
- kanban CSV schema remains valid

## 8. Exit Criteria

A release candidate is QA-passing only when all are true:
- policy checks pass
- mandatory pytest suites pass
- security gate passes
- docs gate passes
- web UI suites pass or are explicitly blocked with evidence and approved risk acceptance

## 9. Incident and Escalation Procedure

If a gate fails or is blocked:
1. Record command, timestamp, environment, and raw output.
2. Update `docs/ROADMAP.md` and `docs/kanban-board.csv`.
3. Open remediation task with owner and due sprint.
4. Re-run full QA set after fix.
5. Attach evidence in sprint log under `docs/dev-logs/`.

## 10. Audit Artifacts

Maintain these artifacts per QA cycle:
- command transcript summary
- test pass/fail snapshot
- blocker evidence (if any)
- remediation linkage
- final release recommendation
