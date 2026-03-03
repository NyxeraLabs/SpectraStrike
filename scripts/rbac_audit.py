#!/usr/bin/env python3

# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SENSITIVE_ROUTES = [
    "ui/web/app/api/actions/runner/kill-all/route.ts",
    "ui/web/app/api/actions/queue/purge/route.ts",
    "ui/web/app/api/actions/auth/revoke-tenant/route.ts",
    "ui/web/app/api/actions/armory/approve/route.ts",
]


def main() -> int:
    findings: list[dict[str, object]] = []
    failures = 0

    for rel in SENSITIVE_ROUTES:
        path = ROOT / rel
        content = path.read_text(encoding="utf-8")
        has_role_guard = "requiredAnyRole" in content
        has_audit_log = "logApiAudit(" in content
        ok = has_role_guard and has_audit_log
        if not ok:
            failures += 1
        findings.append(
            {
                "file": rel,
                "role_guard": has_role_guard,
                "audit_log": has_audit_log,
                "ok": ok,
            }
        )

    result = {"failures": failures, "findings": findings}
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
