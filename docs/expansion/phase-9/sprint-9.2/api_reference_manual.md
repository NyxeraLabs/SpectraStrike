# API Reference Manual - Phase 9 Sprint 9.2

## SpectraStrike UI APIs (selected)
### Auth
- `POST /ui/api/v1/auth/login`
- `POST /ui/api/v1/auth/register`
- `POST /ui/api/v1/auth/logout`
- `POST /ui/api/v1/auth/demo`
- `POST /ui/api/v1/auth/legal/accept`

### Telemetry & Status
- `GET /ui/api/telemetry/events`
- `GET /ui/api/fleet/status`
- `GET /ui/api/defensive/effectiveness`
- `GET /ui/api/policy-trust/status`
- `POST /ui/api/policy-trust/apply`

### Privileged Action APIs (RBAC hardened)
- `POST /ui/api/actions/runner/kill-all` (admin)
- `POST /ui/api/actions/queue/purge` (admin)
- `POST /ui/api/actions/auth/revoke-tenant` (admin)
- `POST /ui/api/actions/armory/approve` (admin/operator)

## VectorVue Client APIs (selected)
### Client read routes
- `GET /api/v1/client/findings`
- `GET /api/v1/client/findings/{finding_id}`
- `GET /api/v1/client/evidence`
- `GET /api/v1/client/evidence/{finding_id}`
- `GET /api/v1/client/reports`
- `GET /api/v1/client/reports/{report_id}/download`
- `GET /api/v1/client/risk`
- `GET /api/v1/client/risk-summary`
- `GET /api/v1/client/risk-trend`
- `GET /api/v1/client/remediation`
- `GET /api/v1/client/remediation-status`

### ML routes
- `GET /ml/client/security-score`
- `GET /ml/client/risk`
- `GET /ml/client/detection-gaps`
- `GET /ml/client/anomalies`
- `POST /ml/client/simulate`

### Compliance routes
- `GET /compliance/frameworks`
- `GET /compliance/{framework}/controls`
- `GET /compliance/{framework}/score`
- `GET /compliance/{framework}/report`
- `GET /compliance/audit-window`
- `POST /audit/session`

## Contracts and Responses
- Auth failures: `401` (unauthorized) or `403` (forbidden/legal gating).
- Paginated client responses: `items`, `page`, `page_size`, `total`.
- ML responses: `score`, `confidence`, `explanation`, `model_version`, `generated_at`.
- Compliance responses: signed envelope with `data` + `signature`.
