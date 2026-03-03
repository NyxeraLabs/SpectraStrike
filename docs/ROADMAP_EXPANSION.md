# SpectraStrike + VectorVue Master Expansion Roadmap (Definitive Build Plan)

**Status:** Internal – Zero Public Exposure Until Completion
**Goal:** Deliver a fully stateful, ATT&CK-native, ASM-driven, detection-validation intelligence platform with measurable assurance scoring and modern graph-native UI.
**Alignment:** Sprint sequence continues from `SpectraStrike/docs/ROADMAP.md` where Sprint 35 is the latest completed sprint. This expansion starts at Sprint 36 and preserves `Phase X Sprint X.Y` identifiers for continuity.

---

# PHASE 0 — VectorVue Core Audit & Telemetry Contract

## Sprint 36 (Phase 0 Sprint 0.1) — vv_core Deep Audit

### Commits

* [x] docs: generate complete vv_core model index
* [x] docs: export ER diagram from vv_core
* [x] docs: list all nullable fields per model
* [x] docs: list all FK relationships
* [x] docs: identify orphaned or unused models
* [x] docs: identify unused scoring-related fields
* [x] docs: identify unused detection-related fields
* [x] docs: identify unused ATT&CK-related fields
* [x] docs: build SpectraStrike → VV field mapping spreadsheet
* [x] test: DB migration dry-run validation

---

## Sprint 37 (Phase 0 Sprint 0.2) — Telemetry Contract v2 Specification

### Commits

* [x] feat: define execution lifecycle enum
* [x] feat: define lifecycle transition rules
* [x] feat: define execution metadata schema
* [x] feat: define asset metadata schema
* [x] feat: define identity metadata schema
* [x] feat: define TTP metadata schema
* [x] feat: define detection metadata schema
* [x] feat: define response metadata schema
* [x] feat: define control metadata schema
* [x] feat: add telemetry schema versioning
* [x] feat: add ingestion validation middleware
* [x] test: contract enforcement unit tests

---

# PHASE 1 — Stateful Execution Engine (SpectraStrike)

## Sprint 38 (Phase 1 Sprint 1.1) — Campaign Architecture

### Commits

* [x] feat: Campaign table
* [x] feat: Campaign configuration model
* [x] feat: Campaign scheduling support
* [x] feat: Campaign status tracking
* [x] feat: CampaignStep table
* [x] feat: TechniqueExecution table
* [x] feat: execution start/stop timestamps
* [x] feat: execution failure reason tracking
* [x] feat: cross-asset execution correlation
* [x] test: campaign lifecycle tests

---

## Sprint 39 (Phase 1 Sprint 1.2) — Identity & Pivot Modeling

### Commits

* [x] feat: identity entity model
* [x] feat: credential material tracking
* [x] feat: privilege level classification
* [x] feat: escalation event tracking
* [x] feat: lateral movement edge modeling
* [x] feat: pivot graph persistence
* [x] feat: compromised account attribution
* [x] test: pivot chain reconstruction tests

---

# PHASE 2 — MITRE ATT&CK Backbone

## Sprint 40 (Phase 2 Sprint 2.1) — ATT&CK Relational Layer

### Commits

* [x] feat: Tactic table
* [x] feat: Technique table
* [x] feat: SubTechnique table
* [x] feat: Technique → Tactic relationship mapping
* [x] feat: Technique → Platform mapping
* [x] feat: Technique → DataSource mapping
* [x] feat: Technique → Mitigation mapping
* [x] feat: Technique → Detection guidance mapping
* [x] feat: ATT&CK import automation pipeline
* [x] test: ATT&CK sync validation tests

---

## Sprint 41 (Phase 2 Sprint 2.2) — Technique Coverage & Scoring

### Commits

* [x] feat: TechniqueCoverage model
* [x] feat: detection presence flag
* [x] feat: detection latency calculation logic
* [x] feat: alert quality weight scoring
* [x] feat: false negative tracking
* [x] feat: response observed flag
* [x] feat: containment observed flag
* [x] feat: technique confidence scoring formula
* [x] feat: technique maturity index
* [x] test: scoring regression tests

---

# PHASE 3 — Detection, Control & SOC Validation

## Sprint 42 (Phase 3 Sprint 3.1) — Control Modeling

### Commits

* [x] feat: ControlVendor table
* [x] feat: ControlInstance table
* [x] feat: ControlType enum
* [x] feat: DetectionEvent table
* [x] feat: alert normalization adapter layer
* [x] feat: alert severity normalization
* [x] feat: detection-to-technique mapping logic
* [x] feat: vendor performance comparison support
* [x] test: detection normalization tests

---

## Sprint 43 (Phase 3 Sprint 3.2) — SOC & IR Readiness

### Commits

* [x] feat: ResponseAction table
* [x] feat: escalation timeline tracking
* [x] feat: time-to-detect metric
* [x] feat: time-to-respond metric
* [x] feat: time-to-contain metric
* [x] feat: SOC effectiveness index calculation
* [x] feat: IR readiness composite score
* [x] feat: SLA violation detection logic
* [x] test: response timing validation tests

---

# PHASE 4 — Attack Surface Management (ASM)

## Sprint 44 (Phase 4 Sprint 4.1) — Asset Discovery Engine

### Commits

* [x] feat: AssetInventory core table
* [x] feat: domain discovery module
* [x] feat: subdomain brute-force module
* [x] feat: IP range ingestion module
* [x] feat: ASN lookup integration
* [x] feat: certificate transparency ingestion
* [x] feat: DNS record normalization
* [x] feat: cloud metadata ingestion (AWS)
* [x] feat: cloud metadata ingestion (Azure)
* [x] feat: cloud metadata ingestion (GCP)
* [x] feat: asset ownership tagging
* [x] feat: asset criticality classification
* [x] test: asset deduplication validation

---

## Sprint 45 (Phase 4 Sprint 4.2) — Exposure Intelligence

### Commits

* [x] feat: ExposureFinding table
* [x] feat: port/service abstraction layer
* [x] feat: service fingerprinting module
* [x] feat: misconfiguration detection rules
* [x] feat: exposure severity scoring formula
* [x] feat: exposure aging tracking
* [x] feat: exposure trend tracking
* [x] test: exposure lifecycle validation tests

---

## Sprint 46 (Phase 4 Sprint 4.3) — ASM → Adversary Bridge

### Commits

* [x] feat: exposure-to-technique mapping engine
* [x] feat: initial access probability scoring
* [x] feat: automated attack path builder
* [x] feat: AttackSurfaceRisk composite index
* [x] feat: ASM-driven campaign suggestion engine
* [x] test: adversary path auto-generation tests

---

# PHASE 5 — Playbooks & Adversary Graph Engine

## Sprint 47 (Phase 5 Sprint 5.1) — Playbook Framework

### Commits

* [x] feat: Playbook table
* [x] feat: PlaybookStep table
* [x] feat: step ordering logic
* [x] feat: conditional branching support
* [x] feat: variable injection support
* [x] feat: wrapper template registry
* [x] feat: reusable technique modules
* [x] feat: execution rollback handling
* [x] test: complex multi-step simulation tests

---

## Sprint 48 (Phase 5 Sprint 5.2) — Adversary Graph Modeling

### Commits

* [x] feat: AttackPath table
* [x] feat: TechniqueLink edge table
* [x] feat: graph traversal engine
* [x] feat: privilege escalation path modeling
* [x] feat: lateral movement path modeling
* [x] feat: identity compromise chain modeling
* [x] feat: full campaign graph reconstruction logic
* [x] test: graph reconstruction validation

---

# PHASE 6 — Advanced Analytics & Assurance

## Sprint 49 (Phase 6 Sprint 6.1) — Coverage Analytics

### Commits

* [x] feat: ATT&CK heatmap generator
* [x] feat: tactic-level coverage score
* [x] feat: technique-level coverage score
* [x] feat: detection effectiveness index
* [x] feat: control reliability score
* [x] feat: historical trend comparison engine
* [x] feat: executive risk summary builder
* [x] test: analytics engine validation

---

## Sprint 50 (Phase 6 Sprint 6.2) — Compliance & Reporting

### Commits

* [x] feat: NIST control mapping
* [x] feat: ISO 27001 control mapping
* [x] feat: SOC2 control mapping
* [x] feat: automated assurance report generator
* [x] feat: signed audit export package
* [x] feat: multi-cycle validation comparison
* [x] test: compliance mapping validation

---

# PHASE 7 — Agent Sensors & Telemetry Expansion

## Sprint 51 (Phase 7 Sprint 7.1) — Sensor Core

### Commits

* [x] feat: cross-platform lightweight agent
* [x] feat: secure TLS transport channel
* [x] feat: mutual authentication support
* [x] feat: signed telemetry verification
* [x] feat: telemetry batching support
* [x] feat: sensor health monitoring service
* [x] feat: remote sensor configuration support
* [x] test: ingestion reliability tests

---

## Sprint 52 (Phase 7 Sprint 7.2) — Behavioral & ML Layer

### Commits

* [x] feat: anomaly correlation engine
* [x] feat: behavioral baseline computation
* [x] feat: detection deviation scoring
* [x] feat: technique anomaly weighting
* [x] feat: ML confidence scoring adjustment
* [x] test: ML regression validation suite

---

# PHASE 8 — Graph-Native UX & Unified Platform Interface

---

# Sprint 53 (Phase 8 Sprint 8.1)

# 🔴 SpectraStrike — Execution & Playbook Graph UI

### Scope: SpectraStrike repo only

### Objective

Build the offensive execution graph system with full drag-and-drop capability.

### Commits

* [x] feat(spectrastrike-ui): graph-core integration (shared graph engine foundation)
* [x] feat(spectrastrike-ui): node-link execution canvas
* [x] feat(spectrastrike-ui): drag-and-drop playbook builder
* [x] feat(spectrastrike-ui): execution node types (initial access, privilege escalation, lateral movement, exfiltration, C2)
* [x] feat(spectrastrike-ui): conditional branching support in graph
* [x] feat(spectrastrike-ui): execution state visualization overlay
* [x] feat(spectrastrike-ui): real-time telemetry streaming panel
* [x] feat(spectrastrike-ui): identity & pivot relationship overlays
* [x] feat(spectrastrike-ui): campaign timeline replay view
* [x] test(spectrastrike-ui): graph execution state validation
* [x] test(spectrastrike-ui): concurrent execution rendering stress test

---

# Sprint 54 (Phase 8 Sprint 8.2)

# 🟢 ASM — Asset & Exposure Graph Engine

### Scope: SpectraStrike repo (ASM module)

### Objective

Graph-native attack surface modeling with drag-and-drop relationships.

### Commits

* [x] feat(asm-ui): asset graph visualization engine
* [x] feat(asm-ui): drag-and-drop asset relationship builder
* [x] feat(asm-ui): exposure-to-asset linking visualization
* [x] feat(asm-ui): vulnerability relationship mapping
* [x] feat(asm-ui): external-to-internal pivot path visualization
* [x] feat(asm-ui): cloud IAM & role relationship graph
* [x] feat(asm-ui): exposure risk overlay scoring visualization
* [x] feat(asm-ui): convert exposure graph → SpectraStrike playbook action
* [x] test(asm-ui): large graph rendering performance test
* [x] test(asm-ui): exposure mapping integrity validation

⚠️ Important:
ASM graph must reuse same graph-core library as SpectraStrike execution graph.

---

# Sprint 55 (Phase 8 Sprint 8.3)

# 🔵 VectorVue — Telemetry Intelligence & Detection Visualization

### Scope: VectorVue repo

### Objective

Interactive intelligence dashboards powered by vv_core schema.

### Commits

* [x] feat(vectorvue-ui): interactive ATT&CK heatmap (coverage vs detection vs response)
* [x] feat(vectorvue-ui): technique confidence score visualization
* [x] feat(vectorvue-ui): detection latency timeline graph
* [x] feat(vectorvue-ui): false negative analysis dashboard
* [x] feat(vectorvue-ui): control validation matrix (EDR/XDR/NGFW/AV)
* [x] feat(vectorvue-ui): SOC performance dashboard (MTTD, MTTR, containment rate)
* [x] feat(vectorvue-ui): telemetry field completeness dashboard
* [x] feat(vectorvue-ui): anomaly & behavioral analytics visualization
* [x] feat(vectorvue-ui): evidence lifecycle tracking interface
* [x] test(vectorvue-ui): telemetry-to-heatmap integrity tests
* [x] test(vectorvue-ui): dashboard rendering performance test

---

# Sprint 56 (Phase 8 Sprint 8.4)

# 🟣 Unified Bundle Experience (Nexus Mode)

### Scope: Integration between SpectraStrike & VectorVue

⚠️ Not a separate repo.
This is the cross-product experience layer.

### Objective

Provide a unified navigation and cross-linking experience.

### Commits

* [x] feat(platform-ui): unified navigation shell (SpectraStrike ↔ VectorVue)
* [x] feat(platform-ui): cross-product deep-link routing
* [x] feat(platform-ui): shared authentication & RBAC layer
* [x] feat(platform-ui): unified activity feed (execution + detection events)
* [x] feat(platform-ui): cross-product search engine
* [x] feat(platform-ui): campaign → detection → assurance drill-down flow
* [x] feat(platform-ui): export unified validation report (execution + detection)
* [x] test(platform-ui): cross-module state synchronization tests

This is what commercially becomes “Nexus” — but technically it's integrated UX.

---

# Sprint 57 (Phase 8 Sprint 8.5)

# 🌐 Global UX System & Feedback Layer

### Scope: Shared design system across both repos

### Objective

Modern, enterprise-grade UX maturity.

### Commits

* [x] feat(global-ui): design system tokens (colors, spacing, typography)
* [x] feat(global-ui): responsive layout framework
* [x] feat(global-ui): global notification & feedback system
* [x] feat(global-ui): role-based UI rendering (Red Team / Blue Team / Exec / Auditor)
* [x] feat(global-ui): real-time system health indicators
* [x] feat(global-ui): keyboard shortcuts & power-user mode
* [x] feat(global-ui): theme system (dark/light enterprise)
* [x] feat(global-ui): persistent workspace state recovery
* [x] test(global-ui): accessibility validation (WCAG)
* [x] test(global-ui): rendering performance benchmark

---

# PHASE 9 — Hardening & Internal Release Readiness

## Sprint 58 (Phase 9 Sprint 9.1) — System Hardening

### Commits

* [x] chore: performance optimization pass
* [x] chore: DB index optimization
* [x] chore: load testing framework
* [x] chore: stress testing scenarios
* [x] chore: security hardening review
* [x] chore: RBAC enforcement audit
* [x] chore: logging & observability refinement
* [x] feat: VectorVue bridge failure diagnostics for E2E audit clarity
* [x] chore: cross-repo license header CI stabilization
* [x] chore: federation startup URL output + portal mjs typing compatibility
* [x] test: full integration test suite

---

## Sprint 59 (Phase 9 Sprint 9.2) — Documentation & Internal Readiness

### Commits

* [x] docs: full architecture documentation
* [x] docs: API reference manual
* [x] docs: playbook authoring guide
* [x] docs: ASM methodology guide
* [x] docs: detection validation methodology
* [x] docs: SOC scoring methodology
* [x] docs: internal operational runbook
* [x] docs: expanded E2E execution audit evidence refresh

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
