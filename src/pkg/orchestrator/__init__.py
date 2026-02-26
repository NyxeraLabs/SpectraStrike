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

"""Orchestrator runtime package."""

from .anti_replay import AntiReplayConfig, AntiReplayGuard, AntiReplayValidationError
from .anti_repudiation import (
    AntiRepudiationError,
    ExecutionIntentLedger,
    ExecutionIntentRecord,
    verify_execution_intent_api,
)
from .audit_trail import AuditTrailRecord, OrchestratorAuditTrail
from .control_plane_integrity import (
    ConfigurationSignatureMismatchError,
    ControlPlaneIntegrityEnforcer,
    ControlPlaneIntegrityError,
    ImmutableConfigurationHistory,
    ImmutableConfigurationHistoryError,
    PolicyHashMismatchError,
    RuntimeBinaryHashMismatchError,
    SignedConfigurationEnvelope,
    StartupIntegrityConfig,
    StartupIntegrityResult,
    UnsignedConfigurationError,
)
from .engine import OrchestratorEngine, TaskSubmissionRequest
from .execution_fingerprint import (
    ExecutionFingerprintError,
    ExecutionFingerprintInput,
    fingerprint_input_from_envelope,
    generate_operator_bound_execution_fingerprint,
    generate_execution_fingerprint,
    validate_execution_fingerprint,
    validate_fingerprint_before_c2_dispatch,
)
from .dual_signature import (
    DualSignatureError,
    HighRiskManifestDualSigner,
    ManifestSignatureBundle,
)
from .event_loop import AsyncEventLoop
from .jws import CompactJWSGenerator, JWSConfig, JWSPayloadError
from .manifest import (
    ManifestSchemaVersionError,
    ManifestSchemaVersionPolicy,
    NonCanonicalManifestError,
    ExecutionManifest,
    ExecutionManifestValidationError,
    ExecutionTaskContext,
    canonical_manifest_json,
    deterministic_manifest_hash,
    parse_and_validate_manifest_submission,
)
from .messaging import (
    BrokerEnvelope,
    InMemoryRabbitBroker,
    PikaRabbitMQTelemetryPublisher,
    PublishAttemptResult,
    PublishStatus,
    RabbitMQConnectionConfig,
    RabbitMQTelemetryPublisher,
    RabbitRoutingModel,
    TelemetryPublisher,
    TelemetryPublishResult,
)
from .opa import (
    OPAClientError,
    OPAConfig,
    OPAAAAPolicyAdapter,
    OPAAuthorizationError,
    OPAExecutionAuthorizer,
)
from .signing import (
    ManifestSigner,
    VaultTransitConfig,
    VaultTransitError,
    VaultTransitSigner,
)
from .task_scheduler import OrchestratorTask, TaskScheduler
from .telemetry_ingestion import TelemetryEvent, TelemetryIngestionPipeline
from .telemetry_schema import (
    ParsedTelemetryEvent,
    TelemetrySchemaError,
    TelemetrySchemaParser,
)
from .vault_hardening import (
    VaultHardeningError,
    VaultHardeningWorkflow,
    VaultRotationResult,
    VaultUnsealPolicy,
    VaultUnsealPolicyError,
)

__all__ = [
    "AsyncEventLoop",
    "OrchestratorTask",
    "TaskScheduler",
    "TelemetryEvent",
    "TelemetryIngestionPipeline",
    "ParsedTelemetryEvent",
    "TelemetrySchemaError",
    "TelemetrySchemaParser",
    "AntiReplayConfig",
    "AntiReplayGuard",
    "AntiReplayValidationError",
    "AntiRepudiationError",
    "ExecutionIntentRecord",
    "ExecutionIntentLedger",
    "verify_execution_intent_api",
    "AuditTrailRecord",
    "OrchestratorAuditTrail",
    "DualSignatureError",
    "ManifestSignatureBundle",
    "HighRiskManifestDualSigner",
    "ControlPlaneIntegrityError",
    "UnsignedConfigurationError",
    "ConfigurationSignatureMismatchError",
    "PolicyHashMismatchError",
    "RuntimeBinaryHashMismatchError",
    "ImmutableConfigurationHistoryError",
    "SignedConfigurationEnvelope",
    "StartupIntegrityConfig",
    "StartupIntegrityResult",
    "ImmutableConfigurationHistory",
    "ControlPlaneIntegrityEnforcer",
    "OrchestratorEngine",
    "TaskSubmissionRequest",
    "ExecutionFingerprintError",
    "ExecutionFingerprintInput",
    "generate_operator_bound_execution_fingerprint",
    "generate_execution_fingerprint",
    "validate_execution_fingerprint",
    "validate_fingerprint_before_c2_dispatch",
    "fingerprint_input_from_envelope",
    "CompactJWSGenerator",
    "JWSConfig",
    "JWSPayloadError",
    "ExecutionTaskContext",
    "ExecutionManifest",
    "ExecutionManifestValidationError",
    "NonCanonicalManifestError",
    "ManifestSchemaVersionError",
    "ManifestSchemaVersionPolicy",
    "canonical_manifest_json",
    "deterministic_manifest_hash",
    "parse_and_validate_manifest_submission",
    "TelemetryPublisher",
    "TelemetryPublishResult",
    "PublishAttemptResult",
    "PublishStatus",
    "BrokerEnvelope",
    "RabbitRoutingModel",
    "RabbitMQConnectionConfig",
    "InMemoryRabbitBroker",
    "RabbitMQTelemetryPublisher",
    "PikaRabbitMQTelemetryPublisher",
    "OPAConfig",
    "OPAClientError",
    "OPAAuthorizationError",
    "OPAExecutionAuthorizer",
    "OPAAAAPolicyAdapter",
    "ManifestSigner",
    "VaultTransitConfig",
    "VaultTransitSigner",
    "VaultTransitError",
    "VaultUnsealPolicy",
    "VaultRotationResult",
    "VaultHardeningError",
    "VaultUnsealPolicyError",
    "VaultHardeningWorkflow",
]
