<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
-->

# SpectraStrike User Guide (Current Implementation)

## 1. Purpose

This guide explains how to operate SpectraStrike with the currently implemented features:

- Core orchestrator and AAA enforcement
- VectorVue integration client and QA smoke checks
- Nmap wrapper integration
- Metasploit wrapper (RPC-oriented)
- Metasploit manual ingestion connector (operator-driven workflow)

## 2. Prerequisites

- Python 3.12+ with virtual environment support
- Installed dependencies from `requirements.txt`
- Nmap available in system path
- Optional: local VectorVue instance
- Optional: local Metasploit web service/API

## 3. Environment Setup

```bash
cd /home/xoce/Workspace/SpectraStrike
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Run Core Test Baseline

```bash
PYTHONPATH=src .venv/bin/pytest -q tests/unit tests/qa
```

## 5. VectorVue Usage

### 5.1 Run Sprint 5 QA smoke checks

```bash
PYTHONPATH=src .venv/bin/python -m pkg.integration.vectorvue.qa_smoke
```

### 5.2 Run live QA tests

```bash
VECTORVUE_QA_LIVE=1 PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_vectorvue_api_qa.py
```

### 5.3 What this validates

- Login and token flow
- Event ingestion endpoint
- Finding ingestion endpoint
- Ingest status polling

## 6. Nmap Integration Usage

Nmap integration is implemented through the wrapper module and telemetry handoff.

### 6.1 Example invocation from Python

```python
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.nmap import NmapScanOptions, NmapWrapper

telemetry = TelemetryIngestionPipeline(batch_size=10)
wrapper = NmapWrapper()

result = wrapper.run_scan(
    NmapScanOptions(
        targets=["127.0.0.1"],
        tcp_syn=True,
        udp_scan=False,
        os_detection=False,
        ports="80,443",
        output_format="xml",
    )
)
event = wrapper.send_to_orchestrator(result, telemetry, actor="operator")
print(result.summary)
print(event.event_type)
```

### 6.2 Notes

- If running unprivileged, the wrapper can fall back from `-sS` to `-sT`.
- Parsed output is normalized and emitted to telemetry pipeline.

## 7. Metasploit Integration Models

### 7.1 Wrapper model (RPC-oriented)

The wrapper in `src/pkg/wrappers/metasploit.py` supports:

- Auth/connect
- Module metadata load
- Exploit execution
- Session output capture
- Telemetry handoff

Use this where RPC execution endpoints are available in your Metasploit runtime.

### 7.2 Manual operator model (recommended for current workflow)

Operators run Metasploit manually, and SpectraStrike ingests results from Metasploit APIs.

Implemented in:

- `src/pkg/integration/metasploit_manual.py`
- `src/pkg/telemetry/sync_metasploit_manual.py`

## 8. Manual Metasploit Ingestion (Operator-Driven)

### 8.1 Workflow

1. Red team operator or pentester executes activities in Metasploit.
2. SpectraStrike sync command pulls sessions and session-events from Metasploit API.
3. SpectraStrike emits normalized telemetry events.
4. Checkpoint is updated to avoid duplicate ingestion on next run.

### 8.2 Run command

```bash
PYTHONPATH=src .venv/bin/python -m pkg.telemetry.sync_metasploit_manual \
  --base-url https://localhost:5443 \
  --username <msf_webservice_user> \
  --password '<msf_webservice_password>' \
  --checkpoint-file .state/metasploit_manual_checkpoint.json
```

### 8.3 Output example

The command prints a summary line similar to:

`METASPLOIT_MANUAL_SYNC observed_sessions=<n> observed_events=<n> emitted=<n> flushed=<n> last_event_id=<id>`

### 8.4 Telemetry event types emitted

- `metasploit_manual_session_observed`
- `metasploit_manual_event_observed`

## 9. Security and Operational Notes

- Use least-privilege credentials for integrations.
- Prefer TLS verification in non-local environments.
- Store API credentials in secure secret management, not shell history.
- Keep checkpoint files persisted in durable storage for production sync jobs.

## 10. Troubleshooting

### 10.1 Nmap permission errors

Symptoms:
- `"requires root privileges"` or socket permission errors

Actions:
- Run with proper privileges where policy allows.
- Keep unprivileged fallback enabled for TCP connect scans.

### 10.2 Metasploit endpoint mismatch

Symptoms:
- Connection/refused or unsupported RPC route errors

Actions:
- Verify whether your Metasploit runtime exposes RPC execution endpoints or only data APIs.
- For manual operations, use `sync_metasploit_manual` flow.

### 10.3 VectorVue validation errors

Symptoms:
- HTTP `422` with `validation_failed`

Actions:
- Align payload with the documented SpectraStrike payload examples.

## 11. Current Feature Coverage Snapshot

- Implemented and QA-covered:
  - VectorVue client + live QA checks
  - Nmap wrapper + QA
  - Metasploit wrapper + QA
  - Metasploit manual ingestion connector + unit coverage
- In progress by roadmap:
  - Async messaging backbone (Kafka/RabbitMQ)
  - Additional wrappers and later-phase integrations
