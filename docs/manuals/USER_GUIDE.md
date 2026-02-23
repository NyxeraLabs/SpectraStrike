<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike User Guide

## 1. Audience and Purpose

This guide is for security operators and platform engineers running SpectraStrike in a local or on-prem Docker environment.

Goals:
- deploy the runtime safely
- operate integrations against remote operator infrastructure
- execute repeatable security and QA controls

## 2. Runtime Topology

Deployed services:
- `app` (orchestrator runtime)
- `nginx` (HTTPS edge, optional mTLS)
- `rabbitmq` (telemetry broker, TLS-only listener)
- `postgres` (state storage, TLS + client-cert verification)
- `redis` (cache/buffer, TLS + client-cert verification)
- `loki` + `vector` (centralized local log pipeline)

Optional tool profile:
- `nmap-tool`
- `metasploit-tool`

## 3. Initial Setup

### 3.1 Prepare environment

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Generate certificates

```bash
make tls-dev-cert
make pki-internal
```

Generated artifacts:
- `docker/nginx/certs/tls.crt`, `docker/nginx/certs/tls.key`
- `docker/pki/ca.crt`
- `docker/pki/rabbitmq/server.crt`, `docker/pki/rabbitmq/server.key`
- `docker/pki/postgres/server.crt`, `docker/pki/postgres/server.key`
- `docker/pki/redis/server.crt`, `docker/pki/redis/server.key`
- `docker/pki/app/client.crt`, `docker/pki/app/client.key`

### 3.3 Configure secrets

Set strong credentials in:
- `docker/secrets/rabbitmq_password.txt`
- `docker/secrets/postgres_password.txt`

## 4. Start and Operate the Stack

### 4.1 Start core stack

```bash
make up
```

### 4.2 Start with tool profile

```bash
make up-all
```

### 4.3 Centralized logs

```bash
make obs-up
make obs-down
```

### 4.4 Stop stack

```bash
make down
```

## 5. Exposed Ports

Configured via `.env`:
- `HOST_PROXY_HTTP_PORT` (default `18080`)
- `HOST_PROXY_TLS_PORT` (default `18443`)
- `HOST_DB_PORT` (default `15432`)
- `HOST_RABBITMQ_MGMT_PORT` (default `15672`)

All other service ports are internal-only by default.

## 6. Remote Integration Configuration

SpectraStrike is remote-operator-first.

### 6.1 Metasploit RPC wrapper

Use env vars:
- `MSF_RPC_HOST`
- `MSF_RPC_PORT`
- `MSF_RPC_SSL`
- `MSF_RPC_USERNAME`
- `MSF_RPC_PASSWORD`
- optional pin: `MSF_RPC_TLS_PINNED_CERT_SHA256`

### 6.2 Manual Metasploit ingestion

Use env vars:
- `MSF_MANUAL_BASE_URL`
- `MSF_MANUAL_USERNAME`
- `MSF_MANUAL_PASSWORD`

Run sync command:

```bash
PYTHONPATH=src .venv/bin/python -m pkg.telemetry.sync_metasploit_manual
```

### 6.3 RabbitMQ publisher

Use env vars:
- `RABBITMQ_HOST`
- `RABBITMQ_PORT` (TLS listener default `5671`)
- `RABBITMQ_USER`
- `RABBITMQ_PASSWORD`
- `RABBITMQ_SSL`
- `RABBITMQ_SSL_CA_FILE`
- `RABBITMQ_SSL_CERT_FILE`
- `RABBITMQ_SSL_KEY_FILE`

## 7. Security Controls and Validation

### 7.1 Baseline checks

```bash
make security-check
make policy-check
```

### 7.2 Supply-chain gate (local, dockerized)

```bash
make sbom
make vuln-scan
make sign-image
make verify-sign
make security-gate
make full-regression
```

### 7.3 Firewall controls (host-level)

```bash
sudo make firewall-apply
sudo make firewall-egress-apply
```

### 7.4 Backup workflows

```bash
make backup-postgres
make backup-redis
make backup-all
```

## 8. Enterprise Security Notes

Implemented:
- ingress TLS and hardened proxy headers
- optional client-certificate validation at edge
- internal mTLS for telemetry broker path (app <-> rabbitmq)
- certificate pinning support in outbound integration clients
- tamper-evident audit chaining
- optional MFA and lockout in AAA framework

In progress:
- full service-to-service mTLS for observability pipeline (`vector` <-> `loki`)

## 9. Troubleshooting

### 9.1 Nginx TLS health fails
- Ensure `make tls-dev-cert` ran successfully.
- Verify `docker/nginx/certs/tls.crt` and `tls.key` exist.

### 9.2 RabbitMQ TLS handshake errors
- Ensure `make pki-internal` ran.
- Verify CA/client cert paths in `.env` (`RABBITMQ_SSL_*`).
- Confirm rabbitmq container has mounted `docker/pki`.

### 9.3 Firewall rules break connectivity
- Re-check allowed ports in `.env`.
- Re-apply with updated values.
- Review host `iptables -S DOCKER-USER` and `iptables -S DOCKER-EGRESS`.

### 9.4 PostgreSQL mTLS connection failures
- Ensure `make pki-internal` was re-run after TLS changes.
- Verify Postgres started with `start-postgres-tls.sh` in compose.
- Confirm client uses CA/client cert/key (`POSTGRES_SSL_*` envs).

### 9.5 Redis mTLS connection failures
- Ensure Redis healthcheck is `redis-cli --tls` and passing.
- Validate mounted cert paths under `/etc/redis/pki` in container.
- Confirm client uses `REDIS_TLS_*` env variables and port `6380`.

## 10. Operational References

- `README.md`
- `SECURITY.md`
- `docs/manuals/ORCHESTRATOR_ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/kanban-board.csv`
