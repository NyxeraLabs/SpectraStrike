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

"""Unit tests for remote endpoint environment configuration."""

from __future__ import annotations

from pkg.integration.metasploit_manual import MetasploitManualConfig
from pkg.orchestrator.messaging import RabbitMQConnectionConfig
from pkg.wrappers.metasploit import MetasploitConfig


def test_metasploit_rpc_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("MSF_RPC_HOST", "10.10.10.20")
    monkeypatch.setenv("MSF_RPC_PORT", "7555")
    monkeypatch.setenv("MSF_RPC_SSL", "false")
    monkeypatch.setenv("MSF_RPC_USERNAME", "operator")
    monkeypatch.setenv("MSF_RPC_PASSWORD", "secret")

    cfg = MetasploitConfig.from_env()

    assert cfg.host == "10.10.10.20"
    assert cfg.port == 7555
    assert cfg.ssl is False
    assert cfg.username == "operator"
    assert cfg.password == "secret"


def test_metasploit_manual_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("MSF_MANUAL_BASE_URL", "https://10.10.10.30:5443")
    monkeypatch.setenv("MSF_MANUAL_USERNAME", "manual")
    monkeypatch.setenv("MSF_MANUAL_PASSWORD", "secret")
    monkeypatch.setenv("MSF_MANUAL_VERIFY_TLS", "false")

    cfg = MetasploitManualConfig.from_env()

    assert cfg.base_url == "https://10.10.10.30:5443"
    assert cfg.username == "manual"
    assert cfg.password == "secret"
    assert cfg.verify_tls is False


def test_rabbit_connection_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("RABBITMQ_HOST", "10.10.10.40")
    monkeypatch.setenv("RABBITMQ_PORT", "5679")
    monkeypatch.setenv("RABBITMQ_USER", "broker-user")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "broker-pass")
    monkeypatch.setenv("RABBITMQ_VHOST", "spectra")

    cfg = RabbitMQConnectionConfig.from_env()

    assert cfg.host == "10.10.10.40"
    assert cfg.port == 5679
    assert cfg.username == "broker-user"
    assert cfg.password == "broker-pass"
    assert cfg.virtual_host == "spectra"
