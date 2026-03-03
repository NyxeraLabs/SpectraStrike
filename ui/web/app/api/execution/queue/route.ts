/*
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
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

import { validateAuthenticatedRequest } from "../../../lib/auth-store";
import { listRuntimeTasks, summarizeRuntimeQueue } from "../../../lib/execution-runtime-store";
import { proxyToOrchestrator } from "../../../lib/orchestrator-proxy";

export async function GET(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json(
      {
        error: authDecision.error ?? "unauthorized",
        legal: authDecision.legal,
      },
      { status }
    );
  }

  const url = new URL(request.url);
  const limit = Number(url.searchParams.get("limit") ?? "100");
  const upstream = await proxyToOrchestrator(`/api/v1/tasks?limit=${encodeURIComponent(String(limit))}`, { method: "GET" });
  if (upstream && upstream.ok) {
    const body = await upstream.json();
    return Response.json(body, { status: 200, headers: { "cache-control": "no-store" } });
  }

  return Response.json(
    {
      items: listRuntimeTasks(limit),
      queue: summarizeRuntimeQueue(),
      source: "ui_runtime_store",
    },
    { status: 200, headers: { "cache-control": "no-store" } }
  );
}
