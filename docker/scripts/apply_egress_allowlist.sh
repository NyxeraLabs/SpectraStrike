#!/bin/sh

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


set -eu

# Host-level egress allowlist for Docker bridge traffic.
# Allows DNS + RFC1918 by default and optional explicit public CIDRs.
# Requires root.

EXTRA_ALLOW_CIDRS="${EGRESS_ALLOW_CIDRS:-}"

iptables -N DOCKER-EGRESS 2>/dev/null || true
iptables -F DOCKER-EGRESS

# Established flows.
iptables -A DOCKER-EGRESS -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow DNS queries from containers.
iptables -A DOCKER-EGRESS -p udp --dport 53 -j ACCEPT
iptables -A DOCKER-EGRESS -p tcp --dport 53 -j ACCEPT

# Allow private network communication.
iptables -A DOCKER-EGRESS -d 10.0.0.0/8 -j ACCEPT
iptables -A DOCKER-EGRESS -d 172.16.0.0/12 -j ACCEPT
iptables -A DOCKER-EGRESS -d 192.168.0.0/16 -j ACCEPT

# Optional explicit public allowlist.
for cidr in ${EXTRA_ALLOW_CIDRS}; do
  iptables -A DOCKER-EGRESS -d "${cidr}" -j ACCEPT
done

# Drop all other egress from docker bridges.
iptables -A DOCKER-EGRESS -j DROP

# Ensure FORWARD chain sends docker bridge egress to allowlist.
iptables -D FORWARD -i docker0 -j DOCKER-EGRESS 2>/dev/null || true
iptables -I FORWARD 1 -i docker0 -j DOCKER-EGRESS

echo "Docker egress allowlist applied"
