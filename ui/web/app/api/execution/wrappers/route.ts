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
import { proxyToOrchestrator } from "../../../lib/orchestrator-proxy";
import { WRAPPER_REGISTRY } from "../../../lib/wrapper-registry";

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

  const upstream = await proxyToOrchestrator("/api/v1/execution/wrappers", { method: "GET" });
  if (upstream && upstream.ok) {
    const body = await upstream.json();
    return Response.json(body, { status: 200, headers: { "cache-control": "no-store" } });
  }

  return Response.json(
    {
      items: WRAPPER_REGISTRY,
      source: "ui_local_registry",
      fallback_reason: "orchestrator_wrapper_registry_unavailable",
    },
    { status: 200, headers: { "cache-control": "no-store" } }
  );
}
