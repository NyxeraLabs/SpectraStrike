#!/bin/sh
set -eu

# Host firewall baseline for Docker-exposed SpectraStrike ports.
# Applies rules to DOCKER-USER chain; run as root.

PROXY_HTTP_PORT="${HOST_PROXY_HTTP_PORT:-18080}"
PROXY_TLS_PORT="${HOST_PROXY_TLS_PORT:-18443}"
DB_PORT="${HOST_DB_PORT:-15432}"

iptables -N DOCKER-USER 2>/dev/null || true
iptables -F DOCKER-USER

# Allow established traffic.
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow loopback and internal docker bridge traffic.
iptables -A DOCKER-USER -i lo -j ACCEPT
iptables -A DOCKER-USER -s 172.16.0.0/12 -j ACCEPT

# Allow explicitly exposed SpectraStrike ports.
iptables -A DOCKER-USER -p tcp --dport "${PROXY_HTTP_PORT}" -j ACCEPT
iptables -A DOCKER-USER -p tcp --dport "${PROXY_TLS_PORT}" -j ACCEPT
iptables -A DOCKER-USER -p tcp --dport "${DB_PORT}" -j ACCEPT

# Drop everything else headed to Docker-published ports.
iptables -A DOCKER-USER -j DROP

echo "DOCKER-USER firewall policy applied"
echo "Allowed TCP ports: ${PROXY_HTTP_PORT}, ${PROXY_TLS_PORT}, ${DB_PORT}"
