<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Wget Wrapper Usage

Module path target: pkg.wrappers.wget.

Expected usage flow:
1. Build validated request input with approved target URL scope.
2. Execute wrapper against approved engagement boundary.
3. Send normalized output to orchestrator telemetry pipeline.
4. Validate live E2E behavior before promoting wrapper state.

Firecracker and Go runner checks:
1. Validate Python firecracker runner contracts:
   `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_firecracker_microvm_runner.py tests/unit/test_universal_edge_runner.py`
2. Validate Go runner firecracker command contract:
   `cd src/runner-go && GOCACHE=/tmp/go-build go test ./runner -run 'TestBuildSandboxCommandUsesFirecrackerSimulation|TestMapToCloudEventIncludesStdoutStderr'`
