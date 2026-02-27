# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
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

"""RabbitMQ-backed forwarding bridge from SpectraStrike telemetry to VectorVue."""

from __future__ import annotations

import hashlib
import json
import ssl
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pkg.integration.vectorvue.client import VectorVueClient
from pkg.logging.framework import emit_integrity_audit_event
from pkg.orchestrator.anti_repudiation import ExecutionIntentLedger
from pkg.orchestrator.execution_fingerprint import (
    fingerprint_input_from_envelope,
    generate_operator_bound_execution_fingerprint,
    validate_fingerprint_before_c2_dispatch,
)
from pkg.orchestrator.messaging import (
    BrokerEnvelope,
    InMemoryRabbitBroker,
    RabbitMQConnectionConfig,
    RabbitRoutingModel,
)

try:
    import pika
except ImportError:  # pragma: no cover - optional dependency for live broker mode
    pika = None


@dataclass(slots=True)
class BridgeDrainResult:
    """Summary of a VectorVue bridge drain execution."""

    consumed: int = 0
    forwarded_events: int = 0
    forwarded_findings: int = 0
    failed: int = 0
    event_statuses: list[str] = field(default_factory=list)
    finding_statuses: list[str] = field(default_factory=list)
    status_poll_statuses: list[str] = field(default_factory=list)


class InMemoryVectorVueBridge:
    """Bridge adapter for in-memory RabbitMQ broker queues."""

    def __init__(
        self,
        *,
        broker: InMemoryRabbitBroker,
        client: VectorVueClient,
        queue: str = "telemetry.events",
        emit_findings_for_all: bool = False,
        replay_nonce_ttl_seconds: int = 120,
        intent_ledger: ExecutionIntentLedger | None = None,
    ) -> None:
        self._broker = broker
        self._client = client
        self._queue = queue
        self._emit_findings_for_all = emit_findings_for_all
        self._replay_nonce_ttl_seconds = replay_nonce_ttl_seconds
        self._seen_nonces: dict[str, datetime] = {}
        self._intent_ledger = intent_ledger or ExecutionIntentLedger()

    def drain(self, limit: int | None = None) -> BridgeDrainResult:
        result = BridgeDrainResult()
        envelopes = self._broker.consume(self._queue, limit=limit)
        for envelope in envelopes:
            result.consumed += 1
            self._forward_one(envelope, result)
        return result

    def _forward_one(self, envelope: BrokerEnvelope, result: BridgeDrainResult) -> None:
        try:
            payload = _build_federated_payload(envelope)
            self._validate_replay_nonce(payload)
            self._record_pre_dispatch_intent(payload)
            response = self._client.send_federated_telemetry(
                payload,
                idempotency_key=payload["execution_hash"],
            )
            result.forwarded_events += 1
            result.event_statuses.append(response.status)
            result.forwarded_findings += 1
            result.finding_statuses.append(response.status)
            result.status_poll_statuses.append(response.status)
        except Exception:
            result.failed += 1

    def _validate_replay_nonce(self, payload: dict[str, Any]) -> None:
        nonce = str(payload["nonce"])
        now = datetime.now(UTC)
        expired_before = now.timestamp() - self._replay_nonce_ttl_seconds
        self._seen_nonces = {
            key: ts for key, ts in self._seen_nonces.items() if ts.timestamp() >= expired_before
        }
        if nonce in self._seen_nonces:
            raise RuntimeError("producer replay detected: nonce already used")
        self._seen_nonces[nonce] = now

    def _record_pre_dispatch_intent(self, payload: dict[str, Any]) -> None:
        attributes = payload["payload"]["attributes"]
        intent = self._intent_ledger.record_pre_dispatch_intent(
            execution_fingerprint=str(payload["execution_hash"]),
            operator_id=str(payload["operator_id"]),
            tenant_id=str(payload["tenant_id"]),
            dispatch_target=str(payload["payload"]["attributes"].get("asset_ref", "orchestrator")),
            manifest_hash=str(attributes.get("manifest_hash", "")),
            tool_hash=str(attributes.get("tool_sha256", "")),
            policy_decision_hash=str(attributes.get("policy_decision_hash", "")),
            timestamp=str(payload["payload"]["observed_at"]),
        )
        payload["payload"]["attributes"]["intent_id"] = intent.intent_id
        payload["payload"]["attributes"]["intent_hash"] = intent.intent_hash
        payload["payload"]["attributes"]["write_ahead"] = True


class PikaVectorVueBridge:
    """Bridge adapter for live RabbitMQ queues via pika basic_get polling."""

    def __init__(
        self,
        *,
        client: VectorVueClient,
        connection: RabbitMQConnectionConfig | None = None,
        routing: RabbitRoutingModel | None = None,
        emit_findings_for_all: bool = False,
        replay_nonce_ttl_seconds: int = 120,
        intent_ledger: ExecutionIntentLedger | None = None,
    ) -> None:
        if pika is None:
            raise RuntimeError("pika package is required for PikaVectorVueBridge")
        self._client = client
        self._connection = connection or RabbitMQConnectionConfig.from_env()
        self._routing = routing or RabbitRoutingModel()
        self._emit_findings_for_all = emit_findings_for_all
        self._replay_nonce_ttl_seconds = replay_nonce_ttl_seconds
        self._seen_nonces: dict[str, datetime] = {}
        self._intent_ledger = intent_ledger or ExecutionIntentLedger()

    def drain(self, limit: int = 100) -> BridgeDrainResult:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        result = BridgeDrainResult()
        connection = self._open_connection()
        try:
            channel = connection.channel()
            queue_name = self._routing.queue
            for _ in range(limit):
                method_frame, _, body = channel.basic_get(queue=queue_name, auto_ack=False)
                if method_frame is None:
                    break

                result.consumed += 1
                envelope = _decode_envelope(body)
                try:
                    payload = _build_federated_payload(envelope)
                    self._validate_replay_nonce(payload)
                    self._record_pre_dispatch_intent(payload)
                    response = self._client.send_federated_telemetry(
                        payload,
                        idempotency_key=payload["execution_hash"],
                    )
                    result.forwarded_events += 1
                    result.event_statuses.append(response.status)
                    result.forwarded_findings += 1
                    result.finding_statuses.append(response.status)
                    result.status_poll_statuses.append(response.status)

                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                except Exception:
                    result.failed += 1
                    channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
        finally:
            connection.close()
        return result

    def _open_connection(self) -> "pika.BlockingConnection":
        credentials = pika.PlainCredentials(
            self._connection.username, self._connection.password
        )
        ssl_options = None
        if self._connection.ssl_enabled:
            context = ssl.create_default_context(cafile=self._connection.ssl_ca_file)
            if self._connection.ssl_cert_file and self._connection.ssl_key_file:
                context.load_cert_chain(
                    certfile=self._connection.ssl_cert_file,
                    keyfile=self._connection.ssl_key_file,
                )
            ssl_options = pika.SSLOptions(context, self._connection.host)
        parameters = pika.ConnectionParameters(
            host=self._connection.host,
            port=self._connection.port,
            virtual_host=self._connection.virtual_host,
            credentials=credentials,
            heartbeat=self._connection.heartbeat,
            blocked_connection_timeout=self._connection.blocked_connection_timeout,
            ssl_options=ssl_options,
        )
        return pika.BlockingConnection(parameters)

    def _validate_replay_nonce(self, payload: dict[str, Any]) -> None:
        nonce = str(payload["nonce"])
        now = datetime.now(UTC)
        expired_before = now.timestamp() - self._replay_nonce_ttl_seconds
        self._seen_nonces = {
            key: ts for key, ts in self._seen_nonces.items() if ts.timestamp() >= expired_before
        }
        if nonce in self._seen_nonces:
            raise RuntimeError("producer replay detected: nonce already used")
        self._seen_nonces[nonce] = now

    def _record_pre_dispatch_intent(self, payload: dict[str, Any]) -> None:
        attributes = payload["payload"]["attributes"]
        intent = self._intent_ledger.record_pre_dispatch_intent(
            execution_fingerprint=str(payload["execution_hash"]),
            operator_id=str(payload["operator_id"]),
            tenant_id=str(payload["tenant_id"]),
            dispatch_target=str(payload["payload"]["attributes"].get("asset_ref", "orchestrator")),
            manifest_hash=str(attributes.get("manifest_hash", "")),
            tool_hash=str(attributes.get("tool_sha256", "")),
            policy_decision_hash=str(attributes.get("policy_decision_hash", "")),
            timestamp=str(payload["payload"]["observed_at"]),
        )
        payload["payload"]["attributes"]["intent_id"] = intent.intent_id
        payload["payload"]["attributes"]["intent_hash"] = intent.intent_hash
        payload["payload"]["attributes"]["write_ahead"] = True


def _decode_envelope(body: bytes) -> BrokerEnvelope:
    parsed = json.loads(body.decode("utf-8"))
    return BrokerEnvelope(
        event_id=str(parsed["event_id"]),
        event_type=str(parsed["event_type"]),
        timestamp=str(parsed["timestamp"]),
        actor=str(parsed["actor"]),
        target=str(parsed["target"]),
        status=str(parsed["status"]),
        attributes=dict(parsed.get("attributes", {})),
        idempotency_key=str(parsed["idempotency_key"]),
        attempt=int(parsed.get("attempt", 1)),
    )


def _parse_timestamp_epoch(timestamp_raw: str) -> int:
    if timestamp_raw.isdigit():
        return int(timestamp_raw)
    normalized = timestamp_raw.replace("Z", "+00:00")
    return int(datetime.fromisoformat(normalized).timestamp())


def _to_attr_value(value: Any) -> str | int | float | bool | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _default_mitre_mapping_for_event(
    event_type: str,
) -> tuple[list[str], list[str]]:
    normalized = event_type.strip().lower()
    mapping: dict[str, tuple[list[str], list[str]]] = {
        "nmap_scan_completed": (["T1595"], ["TA0043"]),
        "metasploit_exploit_completed": (["T1059"], ["TA0002"]),
        "sliver_command_completed": (["T1105"], ["TA0011"]),
        "mythic_task_completed": (["T1059"], ["TA0002"]),
    }
    return mapping.get(normalized, (["T1595"], ["TA0043"]))


def _resolve_mitre_fields(
    *,
    event_type: str,
    attrs: dict[str, Any],
) -> tuple[list[str], list[str]]:
    default_techniques, default_tactics = _default_mitre_mapping_for_event(event_type)
    mitre_techniques_raw = attrs.get("mitre_techniques", default_techniques)
    mitre_tactics_raw = attrs.get("mitre_tactics", default_tactics)
    if not isinstance(mitre_techniques_raw, list) or not mitre_techniques_raw:
        mitre_techniques_raw = default_techniques
    if not isinstance(mitre_tactics_raw, list) or not mitre_tactics_raw:
        mitre_tactics_raw = default_tactics
    techniques = [str(v).upper() for v in mitre_techniques_raw if str(v).strip()]
    tactics = [str(v).upper() for v in mitre_tactics_raw if str(v).strip()]
    return (
        techniques or default_techniques,
        tactics or default_tactics,
    )


def _default_compliance_mapping_for_event(event_type: str) -> dict[str, list[str]]:
    normalized = event_type.strip().lower()
    baseline = {
        "soc2_controls": ["CC7.2", "CC7.3", "A1.2"],
        "iso27001_annex_a_controls": ["A.8.15", "A.8.16", "A.8.24"],
        "nist_800_53_controls": ["AU-2", "AU-8", "SI-4"],
    }
    per_event: dict[str, dict[str, list[str]]] = {
        "nmap_scan_completed": baseline,
        "metasploit_exploit_completed": {
            "soc2_controls": ["CC6.6", "CC7.3", "CC7.4"],
            "iso27001_annex_a_controls": ["A.5.15", "A.8.15", "A.8.24"],
            "nist_800_53_controls": ["AC-3", "AU-2", "AU-10"],
        },
        "sliver_command_completed": {
            "soc2_controls": ["CC6.6", "CC7.3", "CC7.4"],
            "iso27001_annex_a_controls": ["A.5.15", "A.8.15", "A.8.24"],
            "nist_800_53_controls": ["AC-3", "AU-2", "AU-10"],
        },
        "mythic_task_completed": {
            "soc2_controls": ["CC6.6", "CC7.3", "CC7.4"],
            "iso27001_annex_a_controls": ["A.5.15", "A.8.15", "A.8.24"],
            "nist_800_53_controls": ["AC-3", "AU-2", "AU-10"],
        },
    }
    return per_event.get(normalized, baseline)


def _resolve_compliance_fields(
    *,
    event_type: str,
    attrs: dict[str, Any],
) -> dict[str, list[str]]:
    defaults = _default_compliance_mapping_for_event(event_type)
    resolved: dict[str, list[str]] = {}
    for key, default_values in defaults.items():
        raw = attrs.get(key, default_values)
        if not isinstance(raw, list) or not raw:
            raw = default_values
        values = [str(value).upper() for value in raw if str(value).strip()]
        resolved[key] = values or default_values
    return resolved


def _canonical_payload_for_gateway(envelope: BrokerEnvelope) -> dict[str, Any]:
    attrs = dict(envelope.attributes)
    severity = str(attrs.get("severity", "medium")).lower()
    mitre_techniques, mitre_tactics = _resolve_mitre_fields(
        event_type=envelope.event_type,
        attrs=attrs,
    )
    compliance_mapping = _resolve_compliance_fields(
        event_type=envelope.event_type,
        attrs=attrs,
    )
    payload_attributes: dict[str, Any] = {
        "asset_ref": envelope.target,
    }
    for key, value in attrs.items():
        payload_attributes[str(key)] = _to_attr_value(value)
    payload_attributes["soc2_controls"] = ",".join(compliance_mapping["soc2_controls"])
    payload_attributes["iso27001_annex_a_controls"] = ",".join(
        compliance_mapping["iso27001_annex_a_controls"]
    )
    payload_attributes["nist_800_53_controls"] = ",".join(
        compliance_mapping["nist_800_53_controls"]
    )
    return {
        "event_id": envelope.event_id,
        "event_type": envelope.event_type.upper(),
        "source_system": "spectrastrike",
        "severity": severity,
        "observed_at": envelope.timestamp,
        "mitre_techniques": mitre_techniques,
        "mitre_tactics": mitre_tactics,
        "description": str(
            attrs.get(
                "message",
                f"SpectraStrike telemetry event {envelope.event_type} status={envelope.status}",
            )
        ),
        "attributes": payload_attributes,
    }


def _build_event_payload(envelope: BrokerEnvelope) -> dict[str, Any]:
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    tenant_id = str(envelope.attributes.get("tenant_id", ""))
    message = str(
        envelope.attributes.get(
            "message",
            f"SpectraStrike telemetry event {envelope.event_type} status={envelope.status}",
        )
    )
    severity = str(envelope.attributes.get("severity", "medium")).lower()
    return {
        "source_system": "spectrastrike",
        "event_type": envelope.event_type.upper(),
        "occurred_at": envelope.timestamp or now,
        "severity": severity,
        "asset_ref": envelope.target,
        "message": message,
        "metadata": {
            "event_id": envelope.event_id,
            "tenant_id": tenant_id,
            "actor": envelope.actor,
            "status": envelope.status,
            "attempt": envelope.attempt,
            "execution_fingerprint": str(
                envelope.attributes.get("execution_fingerprint", "")
            ),
            "attributes": envelope.attributes,
        },
    }


def _build_finding_payload(envelope: BrokerEnvelope) -> dict[str, Any]:
    status = "open" if envelope.status.lower() in {"failed", "error"} else "triaged"
    first_seen = envelope.timestamp or datetime.now(UTC).isoformat()
    return {
        "title": f"Telemetry finding: {envelope.event_type}",
        "description": (
            f"Derived from broker event {envelope.event_id} "
            f"with status {envelope.status}"
        ),
        "severity": str(envelope.attributes.get("severity", "medium")).lower(),
        "status": status,
        "first_seen": first_seen,
        "asset_ref": envelope.target,
        "recommendation": "Review upstream telemetry and execution context.",
        "metadata": {
            "event_id": envelope.event_id,
            "tenant_id": envelope.attributes.get("tenant_id", ""),
            "actor": envelope.actor,
            "source": "rabbitmq-bridge",
            "execution_fingerprint": str(
                envelope.attributes.get("execution_fingerprint", "")
            ),
            "attestation_measurement_hash": str(
                envelope.attributes.get("attestation_measurement_hash", "")
            ),
        },
    }


def _should_emit_finding(envelope: BrokerEnvelope) -> bool:
    severity = str(envelope.attributes.get("severity", "")).lower()
    return envelope.status.lower() in {"failed", "error"} or severity in {
        "high",
        "critical",
    }


def _build_federated_payload(envelope: BrokerEnvelope) -> dict[str, Any]:
    enriched_attributes = _enrich_fingerprint_attributes(envelope)
    fingerprint_input = fingerprint_input_from_envelope(
        actor=envelope.actor,
        timestamp=envelope.timestamp,
        attributes=enriched_attributes,
    )
    computed = generate_operator_bound_execution_fingerprint(
        data=fingerprint_input, operator_id=envelope.actor
    )
    provided = str(enriched_attributes.get("execution_fingerprint", "")).strip().lower()
    if provided:
        validate_fingerprint_before_c2_dispatch(
            data=fingerprint_input,
            provided_fingerprint=provided,
            actor=envelope.actor,
            dispatch_target=envelope.target,
        )
        execution_fingerprint = provided
    else:
        execution_fingerprint = computed

    emit_integrity_audit_event(
        action="execution_fingerprint_bind",
        actor=envelope.actor,
        target=envelope.target,
        status="success",
        execution_fingerprint=execution_fingerprint,
        event_id=envelope.event_id,
        tenant_id=str(enriched_attributes.get("tenant_id", "")),
    )

    enriched_attributes["execution_fingerprint"] = execution_fingerprint

    enriched_envelope = BrokerEnvelope(
        event_id=envelope.event_id,
        event_type=envelope.event_type,
        timestamp=envelope.timestamp,
        actor=envelope.actor,
        target=envelope.target,
        status=envelope.status,
        attributes=enriched_attributes,
        idempotency_key=envelope.idempotency_key,
        attempt=envelope.attempt,
    )

    campaign_id = str(enriched_attributes.get("campaign_id", "cmp-local")).strip()
    nonce = str(enriched_attributes.get("nonce", envelope.event_id))
    event_payload = _canonical_payload_for_gateway(enriched_envelope)
    event_payload["attributes"]["execution_fingerprint"] = execution_fingerprint
    event_payload["attributes"]["attestation_measurement_hash"] = str(
        enriched_attributes.get("attestation_measurement_hash", "")
    )
    event_payload["attributes"]["schema_version"] = str(
        enriched_attributes.get("schema_version", "1.0")
    )

    return {
        "operator_id": envelope.actor,
        "campaign_id": campaign_id,
        "tenant_id": str(enriched_attributes.get("tenant_id", "")),
        "execution_hash": execution_fingerprint,
        "timestamp": _parse_timestamp_epoch(envelope.timestamp),
        "nonce": nonce,
        "signed_metadata": {
            "tenant_id": str(enriched_attributes.get("tenant_id", "")),
            "operator_id": envelope.actor,
            "campaign_id": campaign_id,
        },
        "payload": event_payload,
    }


def _enrich_fingerprint_attributes(envelope: BrokerEnvelope) -> dict[str, Any]:
    enriched = dict(envelope.attributes)
    if not str(enriched.get("manifest_hash", "")).strip():
        enriched["manifest_hash"] = "mh-" + hashlib.sha256(
            f"{envelope.event_id}|{envelope.event_type}|{envelope.timestamp}".encode(
                "utf-8"
            )
        ).hexdigest()
    if not str(enriched.get("tool_sha256", "")).strip():
        enriched["tool_sha256"] = "sha256:" + hashlib.sha256(
            f"{envelope.target}|{envelope.event_type}".encode("utf-8")
        ).hexdigest()
    if not str(enriched.get("policy_decision_hash", "")).strip():
        enriched["policy_decision_hash"] = "ph-" + hashlib.sha256(
            f"{envelope.actor}|{envelope.status}|{envelope.target}".encode("utf-8")
        ).hexdigest()
    if not str(enriched.get("attestation_measurement_hash", "")).strip():
        enriched["attestation_measurement_hash"] = hashlib.sha256(
            (
                f"{envelope.event_id}|{envelope.timestamp}|"
                f"{envelope.target}|{envelope.actor}|attestation"
            ).encode("utf-8")
        ).hexdigest()
    if not str(enriched.get("tenant_id", "")).strip():
        enriched["tenant_id"] = "unknown-tenant"
    if not str(enriched.get("nonce", "")).strip():
        enriched["nonce"] = envelope.event_id
    return enriched
