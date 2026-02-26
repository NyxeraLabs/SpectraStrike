# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
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

"""CLI bridge for forwarding RabbitMQ telemetry queue items to VectorVue gateway."""

from __future__ import annotations

import argparse
import os

from pkg.integration.vectorvue.client import VectorVueClient
from pkg.integration.vectorvue.config import VectorVueConfig
from pkg.integration.vectorvue.rabbitmq_bridge import PikaVectorVueBridge
from pkg.orchestrator.messaging import RabbitMQConnectionConfig, RabbitRoutingModel


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Drain RabbitMQ telemetry queue and forward to VectorVue"
    )
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--queue", default=os.getenv("RABBITMQ_TELEMETRY_QUEUE", ""))
    parser.add_argument(
        "--emit-findings-for-all",
        action="store_true",
        help="also emit a finding payload for every consumed telemetry message",
    )
    parser.add_argument(
        "--allow-legacy-direct-api",
        action="store_true",
        help="use deprecated direct VectorVue events/findings endpoints",
    )
    parser.add_argument("--base-url", default=os.getenv("VECTORVUE_BASE_URL", "https://127.0.0.1"))
    parser.add_argument("--username", default=os.getenv("VECTORVUE_USERNAME", "acme_viewer"))
    parser.add_argument("--password", default=os.getenv("VECTORVUE_PASSWORD", "AcmeView3r!"))
    parser.add_argument(
        "--tenant-id",
        default=os.getenv("VECTORVUE_TENANT_ID", "10000000-0000-0000-0000-000000000001"),
    )
    parser.add_argument(
        "--verify-tls",
        action="store_true",
        default=os.getenv("VECTORVUE_VERIFY_TLS", "0") == "1",
    )
    parser.add_argument("--timeout-seconds", type=float, default=8.0)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    config = VectorVueConfig(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
        tenant_id=args.tenant_id,
        timeout_seconds=args.timeout_seconds,
        verify_tls=args.verify_tls,
        max_retries=1,
        backoff_seconds=0,
    )
    client = VectorVueClient(config)
    client.login()

    routing = RabbitRoutingModel()
    if args.queue:
        routing = RabbitRoutingModel(
            exchange=routing.exchange,
            routing_key=routing.routing_key,
            queue=args.queue,
            dead_letter_queue=routing.dead_letter_queue,
        )
    bridge = PikaVectorVueBridge(
        client=client,
        connection=RabbitMQConnectionConfig.from_env(),
        routing=routing,
        emit_findings_for_all=args.emit_findings_for_all,
        allow_legacy_direct_api=args.allow_legacy_direct_api,
    )
    result = bridge.drain(limit=args.limit)
    print(
        "VECTORVUE_RABBITMQ_SYNC"
        f" consumed={result.consumed}"
        f" forwarded_events={result.forwarded_events}"
        f" forwarded_findings={result.forwarded_findings}"
        f" failed={result.failed}"
        f" event_statuses={','.join(result.event_statuses)}"
        f" finding_statuses={','.join(result.finding_statuses)}"
        f" status_poll_statuses={','.join(result.status_poll_statuses)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
