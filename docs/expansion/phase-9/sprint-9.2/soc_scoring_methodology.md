# SOC Scoring Methodology - Phase 9 Sprint 9.2

## 1. Scope
SOC scoring quantifies operational defensive performance using campaign-grounded telemetry and response evidence.

## 2. Core Metrics
- **MTTD**: mean time to detect suspicious behavior.
- **MTTR**: mean time to remediate/resolve actions.
- **Containment rate**: percentage of validated scenarios that reached containment.
- **Detection quality**: weighted confidence from technique-level detection outcomes.
- **Backlog pressure**: unresolved remediation and blocked task share.

## 3. Composite Index Pattern
Composite SOC index combines normalized sub-scores:
- Detection Timeliness
- Response Timeliness
- Containment Effectiveness
- Operational Throughput
- False-Negative Pressure

## 4. Calibration Rules
- Recalibrate baseline thresholds quarterly.
- Preserve tenant-specific context to avoid cross-tenant bias.
- Track score drift per campaign cycle for trend analysis.

## 5. Reporting
SOC score outputs should include:
- raw metrics (MTTD/MTTR/containment)
- composite score
- confidence band
- top negative contributors and remediation targets
