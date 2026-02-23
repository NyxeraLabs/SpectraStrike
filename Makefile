# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0
#
# You may:
# Study
# Modify
# Use for internal security testing
#
# You may NOT:
# Offer as a commercial service
# Sell derived competing products

.PHONY: help build up up-all down down-all restart ps logs test test-unit test-integration test-docker qa full-regression prod-up prod-down prod-logs clean tools-up tools-down backup-postgres backup-redis backup-all security-check tls-dev-cert pki-internal firewall-apply firewall-egress-apply sbom vuln-scan sign-image verify-sign policy-check security-gate obs-up obs-down

COMPOSE_DEV = docker compose -f docker-compose.dev.yml
COMPOSE_PROD = docker compose -f docker-compose.prod.yml

help:
	@echo "Available targets:"
	@echo "  build             Build app image"
	@echo "  up                Start dev dockerized stack"
	@echo "  up-all            Start dev stack + dockerized tool profile"
	@echo "  down              Stop dev stack"
	@echo "  down-all          Stop dev stack + tool profile"
	@echo "  restart           Restart dev stack"
	@echo "  ps                Show dev stack status"
	@echo "  logs              Tail dev stack logs"
	@echo "  tools-up          Start dockerized tool containers (nmap/metasploit profile)"
	@echo "  tools-down        Stop dockerized tool containers"
	@echo "  test              Run local test suite (.venv)"
	@echo "  test-unit         Run local unit tests"
	@echo "  test-integration  Run local integration tests"
	@echo "  test-docker       Run test suite inside app container"
	@echo "  qa                Run local and dockerized tests"
	@echo "  full-regression   Run full QA + security + docker test path"
	@echo "  prod-up           Start production compose stack"
	@echo "  prod-down         Stop production compose stack"
	@echo "  prod-logs         Tail production stack logs"
	@echo "  backup-postgres   Backup postgres into ./backup"
	@echo "  backup-redis      Backup redis into ./backup"
	@echo "  backup-all        Backup postgres and redis"
	@echo "  security-check    Validate compose configs and local tests"
	@echo "  tls-dev-cert      Generate local TLS cert/key for nginx"
	@echo "  pki-internal      Generate internal CA + service mTLS certs"
	@echo "  firewall-apply    Apply DOCKER-USER iptables baseline (requires root)"
	@echo "  firewall-egress-apply Apply Docker egress allowlist policy (requires root)"
	@echo "  sbom              Generate SBOM (dockerized syft)"
	@echo "  vuln-scan         Run vulnerability scan (dockerized grype)"
	@echo "  sign-image        Sign image with cosign key (dockerized cosign)"
	@echo "  verify-sign       Verify image signature (dockerized cosign)"
	@echo "  policy-check      Validate compose hardening policy"
	@echo "  security-gate     Run policy + sbom + vuln scan + tests"
	@echo "  obs-up            Start local centralized logging stack (loki/vector)"
	@echo "  obs-down          Stop local centralized logging stack"
	@echo "  clean             Remove dev stack + volumes"

build:
	$(COMPOSE_DEV) build app

up:
	$(COMPOSE_DEV) up -d

up-all:
	$(COMPOSE_DEV) --profile tools up -d

down:
	$(COMPOSE_DEV) down

down-all:
	$(COMPOSE_DEV) --profile tools down

restart: down up

ps:
	$(COMPOSE_DEV) ps

logs:
	$(COMPOSE_DEV) logs -f --tail=100

tools-up:
	$(COMPOSE_DEV) --profile tools up -d nmap-tool metasploit-tool

tools-down:
	$(COMPOSE_DEV) --profile tools stop nmap-tool metasploit-tool

test:
	.venv/bin/pytest -q

test-unit:
	.venv/bin/pytest -q tests/unit

test-integration:
	.venv/bin/pytest -q tests/integration

test-docker:
	$(COMPOSE_DEV) run --rm app python -m pytest -q

qa: test test-docker

full-regression: qa security-gate

backup-postgres:
	./docker/scripts/backup_postgres.sh ./backup

backup-redis:
	./docker/scripts/backup_redis.sh ./backup

backup-all: backup-postgres backup-redis

security-check:
	docker compose -f docker-compose.dev.yml config >/dev/null
	docker compose -f docker-compose.prod.yml config >/dev/null
	.venv/bin/pytest -q

tls-dev-cert:
	./docker/scripts/generate_dev_tls.sh

pki-internal:
	./docker/scripts/generate_internal_pki.sh

firewall-apply:
	./docker/scripts/apply_firewall.sh

firewall-egress-apply:
	./docker/scripts/apply_egress_allowlist.sh

sbom:
	./docker/scripts/security/generate_sbom.sh spectrastrike/app:latest

vuln-scan:
	./docker/scripts/security/scan_vulns.sh spectrastrike/app:latest

sign-image:
	./docker/scripts/security/sign_image.sh spectrastrike/app:latest

verify-sign:
	./docker/scripts/security/verify_image_signature.sh spectrastrike/app:latest

policy-check:
	./docker/scripts/security/check_compose_policy.sh

security-gate: policy-check security-check sbom vuln-scan

obs-up:
	$(COMPOSE_DEV) up -d loki vector

obs-down:
	$(COMPOSE_DEV) stop loki vector

prod-up:
	$(COMPOSE_PROD) up -d

prod-down:
	$(COMPOSE_PROD) down

prod-logs:
	$(COMPOSE_PROD) logs -f --tail=100

clean:
	$(COMPOSE_DEV) down -v --remove-orphans
