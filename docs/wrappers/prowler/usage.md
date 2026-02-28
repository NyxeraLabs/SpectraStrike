<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Prowler Wrapper Usage

Module path target: pkg.wrappers.prowler.

Expected usage flow:
1. Build validated request input.
2. Execute wrapper against authorized target scope.
3. Send normalized output to orchestrator telemetry pipeline.
4. Validate live E2E behavior before promoting wrapper state.

Firecracker and Go runner checks:
1. Validate Python firecracker runner contracts:
   `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_firecracker_microvm_runner.py tests/unit/test_universal_edge_runner.py`
2. Validate Go runner firecracker command contract:
   `cd src/runner-go && GOCACHE=/tmp/go-build go test ./runner -run 'TestBuildSandboxCommandUsesFirecrackerSimulation|TestMapToCloudEventIncludesStdoutStderr'`
