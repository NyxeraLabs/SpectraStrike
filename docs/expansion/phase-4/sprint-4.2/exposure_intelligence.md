# Sprint 45: Exposure Intelligence

## ExposureFinding model
Implemented `ExposureFinding` with typed fields:
- identity: `exposure_id`, `tenant_id`, `asset_id`
- service context: `endpoint`, `fingerprint`
- risk state: `severity_score`, `misconfigurations`, `exploitable`, `public_exposure`
- lifecycle: `first_seen_at`, `last_seen_at`, `status`
- progression: `score_history`

## Port/service abstraction layer
- Added `ServiceEndpoint` model with normalized:
  - `protocol`
  - `port`
  - `service`
  - optional product/version/banner
- Added endpoint normalizer:
  - `normalize_service_endpoint(...)`
  - includes default service inference for common ports.

## Service fingerprinting module
- Added deterministic fingerprint generation:
  - `service_fingerprint(endpoint)`
  - SHA256 over canonical endpoint tuple.

## Misconfiguration detection rules
- Added `detect_misconfigurations(...)` rules:
  - public admin interfaces
  - legacy TLS versions
  - default credentials
  - directory listing
  - weak authentication

## Exposure severity scoring formula
- Added `calculate_exposure_severity(...)` bounded to `0..1`.
- Inputs:
  - service risk weight
  - misconfiguration volume
  - public exposure flag
  - exploitability flag
  - asset criticality multiplier

## Exposure aging and trend tracking
- Added `exposure_age_days(...)`.
- Added `exposure_trend(...)` states:
  - `new`
  - `stable`
  - `increasing`
  - `decreasing`
  - `resolved`
- Added lifecycle operations:
  - `upsert_exposure(...)`
  - `resolve_exposure(...)`

## Validation
- Unit tests cover:
  - endpoint normalization and fingerprint generation
  - misconfiguration rule detection and severity scoring
  - lifecycle updates (open to resolved), age tracking, trend transitions
  - severity-sorted exposure listing
