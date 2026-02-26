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
from .audit_trail import AuditTrailRecord, OrchestratorAuditTrail
from .engine import OrchestratorEngine, TaskSubmissionRequest
from .event_loop import AsyncEventLoop
from .jws import CompactJWSGenerator, JWSConfig, JWSPayloadError
from .manifest import (
    ExecutionManifest,
    ExecutionManifestValidationError,
    ExecutionTaskContext,
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
from .opa import OPAClientError, OPAConfig, OPAAuthorizationError, OPAExecutionAuthorizer
from .signing import (
    ManifestSigner,
    VaultTransitConfig,
    VaultTransitError,
    VaultTransitSigner,
)
from .task_scheduler import OrchestratorTask, TaskScheduler
from .telemetry_ingestion import TelemetryEvent, TelemetryIngestionPipeline

__all__ = [
    "AsyncEventLoop",
    "OrchestratorTask",
    "TaskScheduler",
    "TelemetryEvent",
    "TelemetryIngestionPipeline",
    "AntiReplayConfig",
    "AntiReplayGuard",
    "AntiReplayValidationError",
    "AuditTrailRecord",
    "OrchestratorAuditTrail",
    "OrchestratorEngine",
    "TaskSubmissionRequest",
    "CompactJWSGenerator",
    "JWSConfig",
    "JWSPayloadError",
    "ExecutionTaskContext",
    "ExecutionManifest",
    "ExecutionManifestValidationError",
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
    "ManifestSigner",
    "VaultTransitConfig",
    "VaultTransitSigner",
    "VaultTransitError",
]
