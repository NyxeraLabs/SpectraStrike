# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0
#
# You may:
# Study
# Modify
# Use for internal security testing
#
# You may NOT:
# Offer as a commercial service
# Sell derived competing products

"""CLI entrypoint for manual Metasploit result ingestion into telemetry."""

from __future__ import annotations

import argparse
import os

from pkg.integration.metasploit_manual import (
    IngestionCheckpointStore,
    MetasploitManualClient,
    MetasploitManualConfig,
    MetasploitManualIngestor,
)
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync manual Metasploit activity into SpectraStrike"
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv(
            "MSF_MANUAL_BASE_URL", "https://metasploit.remote.operator:5443"
        ),
    )
    parser.add_argument("--username", default=os.getenv("MSF_MANUAL_USERNAME", ""))
    parser.add_argument("--password", default=os.getenv("MSF_MANUAL_PASSWORD", ""))
    parser.add_argument("--actor", default="red-team-operator")
    parser.add_argument("--verify-tls", action="store_true")
    parser.add_argument(
        "--checkpoint-file", default=".state/metasploit_manual_checkpoint.json"
    )
    parser.add_argument("--batch-size", type=int, default=100)
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if not args.username or not args.password:
        parser.error(
            "username/password required "
            "(or set MSF_MANUAL_USERNAME/MSF_MANUAL_PASSWORD)"
        )
    config = MetasploitManualConfig(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
        verify_tls=args.verify_tls,
    )
    client = MetasploitManualClient(config)
    telemetry = TelemetryIngestionPipeline(batch_size=args.batch_size)
    ingestor = MetasploitManualIngestor(client, telemetry)
    store = IngestionCheckpointStore(args.checkpoint_file)
    checkpoint = store.load()

    result = ingestor.sync(actor=args.actor, checkpoint=checkpoint)
    store.save(result.checkpoint)

    flushed = telemetry.flush_all()
    print(
        "METASPLOIT_MANUAL_SYNC"
        f" observed_sessions={result.observed_sessions}"
        f" observed_events={result.observed_session_events}"
        f" emitted={result.emitted_events}"
        f" flushed={len(flushed)}"
        f" last_event_id={result.checkpoint.last_session_event_id or 'none'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
