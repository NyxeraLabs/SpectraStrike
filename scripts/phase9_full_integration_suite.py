#!/usr/bin/env python3

# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, cmd: list[str], cwd: Path) -> dict[str, object]:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return {
        "name": name,
        "command": cmd,
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-1200:],
        "stderr_tail": proc.stderr[-1200:],
    }


def main() -> int:
    steps: list[dict[str, object]] = []

    steps.append(
        run_step(
            "spectrastrike_ui_unit",
            [
                "npm",
                "run",
                "test:unit",
                "--",
                "--run",
                "tests/unit/auth-store.test.ts",
                "tests/unit/nexus-context-sync.test.ts",
                "tests/unit/global-ui-accessibility-performance.test.ts",
            ],
            ROOT / "ui" / "web",
        )
    )

    steps.append(
        run_step(
            "vectorvue_portal_unit",
            ["npm", "run", "test:unit"],
            ROOT.parent / "VectorVue" / "portal",
        )
    )

    if os.environ.get("PHASE9_RUN_HTTP_QA", "0") == "1":
        steps.append(
            run_step(
                "vectorvue_http_qa",
                [sys.executable, "-m", "unittest", "tests.qa_cycle.test_api_security"],
                ROOT.parent / "VectorVue",
            )
        )

    failed = [step for step in steps if int(step["exit_code"]) != 0]
    summary = {
        "steps": steps,
        "failed_count": len(failed),
        "passed_count": len(steps) - len(failed),
    }
    print(json.dumps(summary, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
