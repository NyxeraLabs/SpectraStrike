<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SSH Wrapper Usage

Module path target: pkg.wrappers.ssh.

Expected usage flow:
1. Build validated request input.
2. Execute wrapper against authorized target scope.
3. Send normalized output to orchestrator telemetry pipeline.
4. Validate live E2E behavior before promoting wrapper state.

Host smoke commands:
1. Dry-run contract path:
   `PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 --timeout-seconds 30 --check-ssh`
2. Live command path:
   `SSH_LIVE_TARGET=localhost SSH_COMMAND='-V' PYTHONPATH=src:/usr/lib/python3.14/site-packages .venv/bin/python -m pkg.integration.host_integration_smoke --tenant-id 10000000-0000-0000-0000-000000000001 --timeout-seconds 30 --check-ssh --check-ssh-live`

Firecracker and Go runner checks:
1. Validate Python firecracker runner contracts:
   `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_firecracker_microvm_runner.py tests/unit/test_universal_edge_runner.py`
2. Validate Go runner firecracker command contract:
   `cd src/runner-go && GOCACHE=/tmp/go-build go test ./runner -run 'TestBuildSandboxCommandUsesFirecrackerSimulation|TestMapToCloudEventIncludesStdoutStderr'`
