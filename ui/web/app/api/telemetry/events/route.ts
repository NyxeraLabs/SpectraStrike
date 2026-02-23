/*
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
*/

import { proxyToOrchestrator } from "../../../lib/orchestrator-proxy";
import { isAuthenticatedRequest } from "../../../lib/auth-store";

const events = [
  {
    event_id: "evt-001",
    source: "nmap",
    status: "success",
    event_type: "nmap_scan_completed",
    actor: "scanner-daemon",
    target: "10.0.9.0/24",
    timestamp: "2026-02-23T18:20:31Z",
  },
  {
    event_id: "evt-002",
    source: "metasploit",
    status: "info",
    event_type: "metasploit_session_ingested",
    actor: "msf-rpc-wrapper",
    target: "workspace/redteam-a",
    timestamp: "2026-02-23T18:19:02Z",
  },
  {
    event_id: "evt-003",
    source: "manual",
    status: "warning",
    event_type: "manual_sync_partial",
    actor: "operator-jmicoli",
    target: "metasploit.remote.operator",
    timestamp: "2026-02-23T18:16:40Z",
  },
];

export async function GET(request: Request) {
  if (!(await isAuthenticatedRequest(request))) {
    return Response.json({ error: "unauthorized" }, { status: 401 });
  }

  const url = new URL(request.url);
  const source = url.searchParams.get("source");
  const status = url.searchParams.get("status");
  const cursor = url.searchParams.get("cursor");

  const upstream = await proxyToOrchestrator(
    `/api/v1/telemetry/events?${new URLSearchParams({
      ...(source ? { source } : {}),
      ...(status ? { status } : {}),
      ...(cursor ? { cursor } : {}),
      limit: "100",
    }).toString()}`,
    { method: "GET" }
  );

  if (upstream && upstream.ok) {
    const body = await upstream.json();
    return Response.json(body, {
      status: 200,
      headers: { "cache-control": "no-store" },
    });
  }

  const filtered = events.filter((item) => {
    if (source && item.source !== source) {
      return false;
    }
    if (status && item.status !== status) {
      return false;
    }
    return true;
  });

  return Response.json(
    {
      items: filtered,
      next_cursor: null,
      mode: "ui-local-fallback",
    },
    { headers: { "cache-control": "no-store" } }
  );
}
