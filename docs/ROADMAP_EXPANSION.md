# SpectraStrike + VectorVue Master Expansion Roadmap (Definitive Build Plan)

**Status:** Internal – Zero Public Exposure Until Completion
**Goal:** Deliver a fully stateful, ATT&CK-native, ASM-driven, detection-validation intelligence platform with measurable assurance scoring and modern graph-native UI.
**Alignment:** Sprint sequence continues from `SpectraStrike/docs/ROADMAP.md` where Sprint 35 is the latest completed sprint. This expansion starts at Sprint 36 and preserves `Phase X Sprint X.Y` identifiers for continuity.

---

# PHASE 0 — VectorVue Core Audit & Telemetry Contract

## Sprint 36 (Phase 0 Sprint 0.1) — vv_core Deep Audit

### Commits

* [ ] docs: generate complete vv_core model index
* [ ] docs: export ER diagram from vv_core
* [ ] docs: list all nullable fields per model
* [ ] docs: list all FK relationships
* [ ] docs: identify orphaned or unused models
* [ ] docs: identify unused scoring-related fields
* [ ] docs: identify unused detection-related fields
* [ ] docs: identify unused ATT&CK-related fields
* [ ] docs: build SpectraStrike → VV field mapping spreadsheet
* [ ] test: DB migration dry-run validation

---

## Sprint 37 (Phase 0 Sprint 0.2) — Telemetry Contract v2 Specification

### Commits

* [ ] feat: define execution lifecycle enum
* [ ] feat: define lifecycle transition rules
* [ ] feat: define execution metadata schema
* [ ] feat: define asset metadata schema
* [ ] feat: define identity metadata schema
* [ ] feat: define TTP metadata schema
* [ ] feat: define detection metadata schema
* [ ] feat: define response metadata schema
* [ ] feat: define control metadata schema
* [ ] feat: add telemetry schema versioning
* [ ] feat: add ingestion validation middleware
* [ ] test: contract enforcement unit tests

---

# PHASE 1 — Stateful Execution Engine (SpectraStrike)

## Sprint 38 (Phase 1 Sprint 1.1) — Campaign Architecture

### Commits

* [ ] feat: Campaign table
* [ ] feat: Campaign configuration model
* [ ] feat: Campaign scheduling support
* [ ] feat: Campaign status tracking
* [ ] feat: CampaignStep table
* [ ] feat: TechniqueExecution table
* [ ] feat: execution start/stop timestamps
* [ ] feat: execution failure reason tracking
* [ ] feat: cross-asset execution correlation
* [ ] test: campaign lifecycle tests

---

## Sprint 39 (Phase 1 Sprint 1.2) — Identity & Pivot Modeling

### Commits

* [ ] feat: identity entity model
* [ ] feat: credential material tracking
* [ ] feat: privilege level classification
* [ ] feat: escalation event tracking
* [ ] feat: lateral movement edge modeling
* [ ] feat: pivot graph persistence
* [ ] feat: compromised account attribution
* [ ] test: pivot chain reconstruction tests

---

# PHASE 2 — MITRE ATT&CK Backbone

## Sprint 40 (Phase 2 Sprint 2.1) — ATT&CK Relational Layer

### Commits

* [ ] feat: Tactic table
* [ ] feat: Technique table
* [ ] feat: SubTechnique table
* [ ] feat: Technique → Tactic relationship mapping
* [ ] feat: Technique → Platform mapping
* [ ] feat: Technique → DataSource mapping
* [ ] feat: Technique → Mitigation mapping
* [ ] feat: Technique → Detection guidance mapping
* [ ] feat: ATT&CK import automation pipeline
* [ ] test: ATT&CK sync validation tests

---

## Sprint 41 (Phase 2 Sprint 2.2) — Technique Coverage & Scoring

### Commits

* [ ] feat: TechniqueCoverage model
* [ ] feat: detection presence flag
* [ ] feat: detection latency calculation logic
* [ ] feat: alert quality weight scoring
* [ ] feat: false negative tracking
* [ ] feat: response observed flag
* [ ] feat: containment observed flag
* [ ] feat: technique confidence scoring formula
* [ ] feat: technique maturity index
* [ ] test: scoring regression tests

---

# PHASE 3 — Detection, Control & SOC Validation

## Sprint 42 (Phase 3 Sprint 3.1) — Control Modeling

### Commits

* [ ] feat: ControlVendor table
* [ ] feat: ControlInstance table
* [ ] feat: ControlType enum
* [ ] feat: DetectionEvent table
* [ ] feat: alert normalization adapter layer
* [ ] feat: alert severity normalization
* [ ] feat: detection-to-technique mapping logic
* [ ] feat: vendor performance comparison support
* [ ] test: detection normalization tests

---

## Sprint 43 (Phase 3 Sprint 3.2) — SOC & IR Readiness

### Commits

* [ ] feat: ResponseAction table
* [ ] feat: escalation timeline tracking
* [ ] feat: time-to-detect metric
* [ ] feat: time-to-respond metric
* [ ] feat: time-to-contain metric
* [ ] feat: SOC effectiveness index calculation
* [ ] feat: IR readiness composite score
* [ ] feat: SLA violation detection logic
* [ ] test: response timing validation tests

---

# PHASE 4 — Attack Surface Management (ASM)

## Sprint 44 (Phase 4 Sprint 4.1) — Asset Discovery Engine

### Commits

* [ ] feat: AssetInventory core table
* [ ] feat: domain discovery module
* [ ] feat: subdomain brute-force module
* [ ] feat: IP range ingestion module
* [ ] feat: ASN lookup integration
* [ ] feat: certificate transparency ingestion
* [ ] feat: DNS record normalization
* [ ] feat: cloud metadata ingestion (AWS)
* [ ] feat: cloud metadata ingestion (Azure)
* [ ] feat: cloud metadata ingestion (GCP)
* [ ] feat: asset ownership tagging
* [ ] feat: asset criticality classification
* [ ] test: asset deduplication validation

---

## Sprint 45 (Phase 4 Sprint 4.2) — Exposure Intelligence

### Commits

* [ ] feat: ExposureFinding table
* [ ] feat: port/service abstraction layer
* [ ] feat: service fingerprinting module
* [ ] feat: misconfiguration detection rules
* [ ] feat: exposure severity scoring formula
* [ ] feat: exposure aging tracking
* [ ] feat: exposure trend tracking
* [ ] test: exposure lifecycle validation tests

---

## Sprint 46 (Phase 4 Sprint 4.3) — ASM → Adversary Bridge

### Commits

* [ ] feat: exposure-to-technique mapping engine
* [ ] feat: initial access probability scoring
* [ ] feat: automated attack path builder
* [ ] feat: AttackSurfaceRisk composite index
* [ ] feat: ASM-driven campaign suggestion engine
* [ ] test: adversary path auto-generation tests

---

# PHASE 5 — Playbooks & Adversary Graph Engine

## Sprint 47 (Phase 5 Sprint 5.1) — Playbook Framework

### Commits

* [ ] feat: Playbook table
* [ ] feat: PlaybookStep table
* [ ] feat: step ordering logic
* [ ] feat: conditional branching support
* [ ] feat: variable injection support
* [ ] feat: wrapper template registry
* [ ] feat: reusable technique modules
* [ ] feat: execution rollback handling
* [ ] test: complex multi-step simulation tests

---

## Sprint 48 (Phase 5 Sprint 5.2) — Adversary Graph Modeling

### Commits

* [ ] feat: AttackPath table
* [ ] feat: TechniqueLink edge table
* [ ] feat: graph traversal engine
* [ ] feat: privilege escalation path modeling
* [ ] feat: lateral movement path modeling
* [ ] feat: identity compromise chain modeling
* [ ] feat: full campaign graph reconstruction logic
* [ ] test: graph reconstruction validation

---

# PHASE 6 — Advanced Analytics & Assurance

## Sprint 49 (Phase 6 Sprint 6.1) — Coverage Analytics

### Commits

* [ ] feat: ATT&CK heatmap generator
* [ ] feat: tactic-level coverage score
* [ ] feat: technique-level coverage score
* [ ] feat: detection effectiveness index
* [ ] feat: control reliability score
* [ ] feat: historical trend comparison engine
* [ ] feat: executive risk summary builder
* [ ] test: analytics engine validation

---

## Sprint 50 (Phase 6 Sprint 6.2) — Compliance & Reporting

### Commits

* [ ] feat: NIST control mapping
* [ ] feat: ISO 27001 control mapping
* [ ] feat: SOC2 control mapping
* [ ] feat: automated assurance report generator
* [ ] feat: signed audit export package
* [ ] feat: multi-cycle validation comparison
* [ ] test: compliance mapping validation

---

# PHASE 7 — Agent Sensors & Telemetry Expansion

## Sprint 51 (Phase 7 Sprint 7.1) — Sensor Core

### Commits

* [ ] feat: cross-platform lightweight agent
* [ ] feat: secure TLS transport channel
* [ ] feat: mutual authentication support
* [ ] feat: signed telemetry verification
* [ ] feat: telemetry batching support
* [ ] feat: sensor health monitoring service
* [ ] feat: remote sensor configuration support
* [ ] test: ingestion reliability tests

---

## Sprint 52 (Phase 7 Sprint 7.2) — Behavioral & ML Layer

### Commits

* [ ] feat: anomaly correlation engine
* [ ] feat: behavioral baseline computation
* [ ] feat: detection deviation scoring
* [ ] feat: technique anomaly weighting
* [ ] feat: ML confidence scoring adjustment
* [ ] test: ML regression validation suite

---

# PHASE 8 — Modern Graph-Native UI & UX

## Sprint 53 (Phase 8 Sprint 8.1) — Workflow & Visualization

### Commits

* [ ] feat: node-link execution canvas
* [ ] feat: drag-and-drop playbook builder
* [ ] feat: real-time execution feedback panel
* [ ] feat: interactive attack path visualization
* [ ] feat: interactive ATT&CK heatmap UI
* [ ] feat: exposure visualization dashboard
* [ ] feat: campaign timeline visualization
* [ ] test: UI state consistency tests

---

## Sprint 54 (Phase 8 Sprint 8.2) — Dashboards & Reporting UX

### Commits

* [ ] feat: responsive dashboard framework
* [ ] feat: executive summary dashboard
* [ ] feat: SOC performance dashboard
* [ ] feat: control vendor comparison dashboard
* [ ] feat: compliance & assurance dashboard
* [ ] feat: exportable PDF/JSON reporting module
* [ ] feat: full user feedback & notification system
* [ ] test: UI performance validation

---

# PHASE 9 — Hardening & Internal Release Readiness

## Sprint 55 (Phase 9 Sprint 9.1) — System Hardening

### Commits

* [ ] chore: performance optimization pass
* [ ] chore: DB index optimization
* [ ] chore: load testing framework
* [ ] chore: stress testing scenarios
* [ ] chore: security hardening review
* [ ] chore: RBAC enforcement audit
* [ ] chore: logging & observability refinement
* [ ] test: full integration test suite

---

## Sprint 56 (Phase 9 Sprint 9.2) — Documentation & Internal Readiness

### Commits

* [ ] docs: full architecture documentation
* [ ] docs: API reference manual
* [ ] docs: playbook authoring guide
* [ ] docs: ASM methodology guide
* [ ] docs: detection validation methodology
* [ ] docs: SOC scoring methodology
* [ ] docs: internal operational runbook

---

# END STATE

* SpectraStrike is fully stateful, campaign-aware, TTP-native.
* VectorVue fully leverages its granular intelligence schema.
* ASM continuously drives adversary simulation planning.
* Detection & response effectiveness are measurable.
* SOC & IR readiness are quantified.
* Assurance & compliance are automated.
* Sensors validate real defensive capability.
* UI is modern, responsive, graph-native, and feedback-driven.

No public exposure until 100% roadmap completion.
