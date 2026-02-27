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
import { validateAuthenticatedRequest } from "../../../lib/auth-store";

const fallbackMetrics = {
  total_events: 240,
  blocked_events: 101,
  successful_events: 139,
  detection_rate: 0.671,
  prevention_rate: 0.421,
  feedback_coverage: 0.583,
  applied_adjustments: 37,
  mode: "ui-local-fallback",
};

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

  const upstream = await proxyToOrchestrator(
    "/api/v1/defensive/effectiveness",
    { method: "GET" }
  );
  if (upstream && upstream.ok) {
    const body = await upstream.json();
    return Response.json(body, {
      status: 200,
      headers: { "cache-control": "no-store" },
    });
  }

  return Response.json(fallbackMetrics, {
    headers: { "cache-control": "no-store" },
  });
}
