<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike QA Runbook
![SpectraStrike Logo](../../ui/web/assets/images/SprectraStrike_Logo.png)


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

6. Internal mTLS verification (DB/cache/broker)

```bash
docker compose -f docker-compose.dev.yml exec -T redis redis-cli --tls --cacert /etc/redis/pki/ca.crt --cert /etc/redis/pki/app/client.crt --key /etc/redis/pki/app/client.key -p 6380 ping
docker compose -f docker-compose.dev.yml exec -T postgres psql "host=postgres dbname=spectrastrike user=$(cat docker/secrets/postgres_user.txt) sslmode=verify-ca sslrootcert=/etc/postgresql/pki/ca.crt sslcert=/etc/postgresql/pki/app/client.crt sslkey=/etc/postgresql/pki/app/client.key" -c "select version();"
docker compose -f docker-compose.dev.yml exec -T app python -c "from pkg.orchestrator.messaging import RabbitMQPublisher; print('rabbitmq tls config loaded')"
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
