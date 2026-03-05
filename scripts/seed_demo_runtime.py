# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

from __future__ import annotations

import argparse
import json
import os
import random
import string
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


@dataclass(slots=True)
class Wrapper:
    key: str
    label: str
    node_type: str


def _default_export_path() -> Path:
    explicit = os.getenv("SPECTRASTRIKE_VECTORVUE_SEED_EXPORT", "").strip()
    if explicit:
        return Path(explicit).expanduser()
    cwd = Path.cwd()
    if (cwd / "scripts").exists():
        return cwd / "local_federation" / "seed" / "spectrastrike_seed_contract.json"
    return Path("/tmp") / "spectrastrike_seed_contract.json"


def _accept_legal(session: requests.Session, api_base: str) -> None:
    payload = {
        "accepted_by": os.getenv("SPECTRASTRIKE_LEGAL_ACCEPTED_BY", "demo-seed"),
        "accepted_documents": {
            "eula": "2026.1",
            "aup": "2026.1",
            "privacy": "2026.1",
        },
    }
    response = session.post(
        f"{api_base}/v1/auth/legal/accept",
        json=payload,
        timeout=15,
        verify=False,
        allow_redirects=False,
    )
    if response.status_code not in {200, 202}:
        response.raise_for_status()


def _candidate_base_urls(base_url: str) -> list[str]:
    candidates = [
        base_url.rstrip("/"),
        os.getenv("SPECTRASTRIKE_UI_API_BASE_URL", "").rstrip("/"),
        os.getenv("UI_ADMIN_API_BASE_URL", "").rstrip("/"),
        "https://nginx:8443/ui/api",
        "https://spectrastrike_nginx:8443/ui/api",
        "http://ui-web:3000/ui/api",
        "http://spectrastrike_ui_web:3000/ui/api",
        "https://127.0.0.1:18443/ui/api",
        "https://localhost:18443/ui/api",
        "http://127.0.0.1:3000/ui/api",
        "http://localhost:3000/ui/api",
    ]
    out: list[str] = []
    for item in candidates:
        if item not in out:
            out.append(item)
    return out


def _try_bootstrap_login(session: requests.Session, api_base: str) -> str:
    username = os.getenv("UI_AUTH_BOOTSTRAP_USERNAME", "operator")
    password = os.getenv("UI_AUTH_BOOTSTRAP_PASSWORD", "Operator!ChangeMe123")
    res = session.post(
        f"{api_base}/v1/auth/login",
        json={"username": username, "password": password},
        timeout=15,
        verify=False,
        allow_redirects=False,
    )
    if 300 <= res.status_code < 400:
        raise RuntimeError(
            f"http_{res.status_code}_redirect_to_{res.headers.get('location', '')}"
        )
    if res.status_code == 403:
        body = {}
        try:
            body = res.json()
        except Exception:  # noqa: BLE001
            body = {}
        if isinstance(body, dict) and body.get("error") == "LEGAL_ACCEPTANCE_REQUIRED":
            _accept_legal(session, api_base)
            res = session.post(
                f"{api_base}/v1/auth/login",
                json={"username": username, "password": password},
                timeout=15,
                verify=False,
                allow_redirects=False,
            )
    res.raise_for_status()
    token = str(res.json().get("access_token", "")).strip()
    if not token:
        raise RuntimeError("bootstrap login did not return access token")
    return token


def _token(session: requests.Session, base_url: str) -> tuple[str, str]:
    last_error = "unknown_error"
    for api_base in _candidate_base_urls(base_url):
        for _ in range(20):
            try:
                return _try_bootstrap_login(session, api_base), api_base
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}:{exc}"
                time.sleep(0.8)
    raise RuntimeError(f"unable to authenticate demo session against any API endpoint: {last_error}")


def _wrappers(session: requests.Session, base_url: str, token: str) -> list[Wrapper]:
    res = session.get(
        f"{base_url}/execution/wrappers",
        headers={"authorization": f"Bearer {token}"},
        timeout=15,
        verify=False,
        allow_redirects=False,
    )
    res.raise_for_status()
    data = res.json()
    items = data.get("items", []) if isinstance(data, dict) else []
    out: list[Wrapper] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", "")).strip()
        if not key:
            continue
        out.append(
            Wrapper(
                key=key,
                label=str(item.get("label", key)).strip(),
                node_type=str(item.get("nodeType", "initial_access")).strip() or "initial_access",
            )
        )
    return out


def _seed_tenant(
    session: requests.Session,
    base_url: str,
    token: str,
    tenant_id: str,
    wrappers: list[Wrapper],
    target_prefix: str,
) -> tuple[int, list[dict[str, object]], list[dict[str, object]]]:
    sample = wrappers[:12]
    nodes = []
    edges = []
    queue: list[str] = []
    for idx, wrapper in enumerate(sample):
        node_id = f"{tenant_id[:8]}-n-{idx+1}-{wrapper.key}"
        nodes.append(
            {
                "id": node_id,
                "label": wrapper.label,
                "technique": f"T{1000 + idx}",
                "nodeType": wrapper.node_type,
                "wrapperKey": wrapper.key,
            }
        )
        queue.append(node_id)
        if idx > 0:
            edges.append(
                {
                    "id": f"{tenant_id[:8]}-e-{idx}",
                    "sourceId": nodes[idx - 1]["id"],
                    "targetId": node_id,
                    "branchCondition": "on_success" if idx % 2 == 0 else "always",
                }
            )

    playbook_payload = {
        "tenant_id": tenant_id,
        "nodes": nodes,
        "edges": edges,
        "queue": queue,
    }
    pb = session.put(
        f"{base_url}/execution/playbook",
        headers={
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
        },
        data=json.dumps(playbook_payload),
        timeout=20,
        verify=False,
        allow_redirects=False,
    )
    pb.raise_for_status()

    failures = 0
    seeded_events: list[dict[str, object]] = []
    seeded_findings: list[dict[str, object]] = []
    for idx, wrapper in enumerate(sample):
        random_suffix = "".join(random.choice(string.ascii_lowercase) for _ in range(4))
        target = f"{target_prefix}.{idx+10}.{random_suffix}.corp.local"
        payload = {
            "tenant_id": tenant_id,
            "tool": wrapper.key,
            "target": target,
            "parameters": {
                "campaign": f"seeded-campaign-{tenant_id[:8]}",
                "demoMode": True,
                "technique": f"T{1000 + idx}",
            },
        }
        submitted = False
        last_error = "unknown"
        task_body: dict[str, object] = {}
        for attempt in range(1, 13):
            try:
                task = session.post(
                    f"{base_url}/actions/tasks",
                    headers={
                        "authorization": f"Bearer {token}",
                        "content-type": "application/json",
                    },
                    data=json.dumps(payload),
                    timeout=20,
                    verify=False,
                    allow_redirects=False,
                )
                if task.status_code in {502, 503, 504, 429}:
                    last_error = f"http_{task.status_code}"
                    time.sleep(min(1.6 * attempt, 8.0))
                    continue
                task.raise_for_status()
                parsed = task.json()
                task_body = parsed if isinstance(parsed, dict) else {}
                submitted = True
                break
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}:{exc}"
                time.sleep(min(1.2 * attempt, 8.0))
        if not submitted:
            failures += 1
            print(
                f"WARNING: task seed failed tenant={tenant_id} tool={wrapper.key} "
                f"target={target} error={last_error}"
            )
            continue

        task_id = str(task_body.get("task_id", "")).strip() or f"seed-task-{tenant_id[:8]}-{idx+1}"
        status = str(task_body.get("status", "queued")).strip().lower() or "queued"
        severity = "critical" if idx % 9 == 0 else "high" if idx % 3 == 0 else "medium"
        envelope_id = f"env-{task_id}"
        attestation_hash = uuid5(NAMESPACE_URL, f"{tenant_id}:{task_id}:attestation").hex
        policy_hash = uuid5(NAMESPACE_URL, f"{tenant_id}:{task_id}:policy").hex
        occurred_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - ((len(sample) - idx) * 11)))
        event_uid = f"evt-{tenant_id[:8]}-{idx+1:03d}"
        request_id = str(uuid5(NAMESPACE_URL, f"spectrastrike-seed:{tenant_id}:{idx+1}"))

        seeded_events.append(
            {
                "request_id": request_id,
                "event_uid": event_uid,
                "source_system": "spectrastrike",
                "event_type": f"task.{status}",
                "occurred_at": occurred_at,
                "severity": severity,
                "asset_ref": target,
                "message": f"{wrapper.label} dispatched to {target}",
                "metadata_json": {
                    "tenant_id": tenant_id,
                    "task_id": task_id,
                    "tool": wrapper.key,
                    "technique": f"T{1000 + idx}",
                    "campaign_id": f"seeded-campaign-{tenant_id[:8]}",
                    "envelope_id": envelope_id,
                    "signature_state": "verified",
                    "attestation_measurement_hash": attestation_hash,
                    "policy_decision_hash": policy_hash,
                    "status": status,
                },
                "raw_payload": {
                    "task_submission": payload,
                    "task_response": task_body,
                },
            }
        )
        if idx % 4 == 0:
            seeded_findings.append(
                {
                    "request_id": request_id,
                    "finding_uid": f"fnd-{tenant_id[:8]}-{idx+1:03d}",
                    "title": f"Telemetry finding: {wrapper.label}",
                    "description": f"Derived from seeded task {task_id} ({wrapper.key})",
                    "severity": severity,
                    "status": "open" if severity in {"critical", "high"} else "triaged",
                    "first_seen": occurred_at,
                    "last_seen": occurred_at,
                    "asset_ref": target,
                    "recommendation": "Review execution telemetry and validate control coverage.",
                    "metadata_json": {
                        "tenant_id": tenant_id,
                        "event_uid": event_uid,
                        "task_id": task_id,
                        "envelope_id": envelope_id,
                    },
                    "raw_payload": {
                        "tool": wrapper.key,
                        "target": target,
                        "status": status,
                    },
                }
            )

    return failures, seeded_events, seeded_findings


def _write_seed_contract(
    *,
    export_path: Path,
    tenant_a: str,
    tenant_b: str,
    events_a: list[dict[str, object]],
    events_b: list[dict[str, object]],
    findings_a: list[dict[str, object]],
    findings_b: list[dict[str, object]],
) -> Path:
    payload = {
        "schema_version": "spectrastrike.demo.seed.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tenants": [
            {
                "tenant_id": tenant_a,
                "events": events_a,
                "findings": findings_a,
            },
            {
                "tenant_id": tenant_b,
                "events": events_b,
                "findings": findings_b,
            },
        ],
    }
    body = json.dumps(payload, indent=2)
    candidates = [export_path, Path("/tmp") / "spectrastrike_seed_contract.json"]
    last_error: Exception | None = None
    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text(body, encoding="utf-8")
            if candidate != export_path:
                print(
                    f"WARNING: unable to write seed contract to {export_path}; "
                    f"used fallback {candidate}"
                )
            return candidate
        except OSError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise RuntimeError("unable to persist seed contract")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed SpectraStrike demo runtime for two tenants.")
    parser.add_argument("--base-url", default="https://127.0.0.1:18443/ui/api")
    parser.add_argument("--tenant-a", default="10000000-0000-0000-0000-000000000001")
    parser.add_argument("--tenant-b", default="20000000-0000-0000-0000-000000000002")
    parser.add_argument("--strict", action="store_true", help="Fail when all task submissions fail for a tenant.")
    parser.add_argument("--export-contract", default=str(_default_export_path()))
    args = parser.parse_args()

    session = requests.Session()
    token, resolved_base = _token(session, args.base_url)
    wrappers = _wrappers(session, resolved_base, token)
    if not wrappers:
        raise RuntimeError("wrapper registry is empty; cannot seed demo runtime")

    failures_a, events_a, findings_a = _seed_tenant(session, resolved_base, token, args.tenant_a, wrappers, "acme")
    failures_b, events_b, findings_b = _seed_tenant(session, resolved_base, token, args.tenant_b, wrappers, "globex")

    total = min(12, len(wrappers))
    if failures_a:
        print(f"WARNING: tenant={args.tenant_a} failed task submissions: {failures_a}/{total}")
    if failures_b:
        print(f"WARNING: tenant={args.tenant_b} failed task submissions: {failures_b}/{total}")

    if args.strict and (failures_a >= total or failures_b >= total):
        raise RuntimeError("strict mode: at least one tenant failed all task submissions")

    export_path = _write_seed_contract(
        export_path=Path(args.export_contract).expanduser(),
        tenant_a=args.tenant_a,
        tenant_b=args.tenant_b,
        events_a=events_a,
        events_b=events_b,
        findings_a=findings_a,
        findings_b=findings_b,
    )
    print(
        "Seed contract written for VectorVue federation import: "
        f"{export_path} (events={len(events_a) + len(events_b)}, findings={len(findings_a) + len(findings_b)})"
    )
    print("SpectraStrike demo runtime seeded for two tenants (with resilient fallback).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
