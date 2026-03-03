# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

from __future__ import annotations

import argparse
import json
import random
import string
from dataclasses import dataclass

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


@dataclass(slots=True)
class Wrapper:
    key: str
    label: str
    node_type: str


def _token(session: requests.Session, base_url: str) -> str:
    res = session.post(
        f"{base_url}/v1/auth/demo",
        headers={"origin": base_url.replace("/ui/api", "/ui")},
        timeout=15,
        verify=False,
    )
    res.raise_for_status()
    body = res.json()
    token = str(body.get("access_token", "")).strip()
    if not token:
        raise RuntimeError("demo auth did not return access_token")
    return token


def _wrappers(session: requests.Session, base_url: str, token: str) -> list[Wrapper]:
    res = session.get(
        f"{base_url}/execution/wrappers",
        headers={"authorization": f"Bearer {token}"},
        timeout=15,
        verify=False,
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
) -> None:
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
            "origin": base_url.replace("/ui/api", "/ui"),
        },
        data=json.dumps(playbook_payload),
        timeout=20,
        verify=False,
    )
    pb.raise_for_status()

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
        task = session.post(
            f"{base_url}/actions/tasks",
            headers={
                "authorization": f"Bearer {token}",
                "content-type": "application/json",
                "origin": base_url.replace("/ui/api", "/ui"),
            },
            data=json.dumps(payload),
            timeout=20,
            verify=False,
        )
        task.raise_for_status()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed SpectraStrike demo runtime for two tenants.")
    parser.add_argument("--base-url", default="https://127.0.0.1:18443/ui/api")
    parser.add_argument("--tenant-a", default="10000000-0000-0000-0000-000000000001")
    parser.add_argument("--tenant-b", default="20000000-0000-0000-0000-000000000002")
    args = parser.parse_args()

    session = requests.Session()
    token = _token(session, args.base_url)
    wrappers = _wrappers(session, args.base_url, token)
    if not wrappers:
        raise RuntimeError("wrapper registry is empty; cannot seed demo runtime")

    _seed_tenant(session, args.base_url, token, args.tenant_a, wrappers, "acme")
    _seed_tenant(session, args.base_url, token, args.tenant_b, wrappers, "globex")
    print("SpectraStrike demo runtime seeded for two tenants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
