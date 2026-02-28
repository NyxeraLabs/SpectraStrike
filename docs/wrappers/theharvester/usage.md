<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# theHarvester Wrapper Usage

Module path target: pkg.wrappers.theharvester.

Expected usage flow:
1. Build validated request input.
2. Execute wrapper against authorized target scope.
3. Send normalized output to orchestrator telemetry pipeline.
4. Validate live E2E behavior before promoting wrapper state.
