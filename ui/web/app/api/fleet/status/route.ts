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

import { validateAuthenticatedRequest } from "../../../lib/auth-store";

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

  return Response.json(
    {
      runners: {
        online: 18,
        degraded: 2,
        offline: 1,
      },
      microvms: {
        active: 41,
        cold_pool: 8,
      },
      queues: {
        telemetry_events_depth: 12,
        dead_letter_depth: 1,
      },
    },
    { status: 200 }
  );
}
