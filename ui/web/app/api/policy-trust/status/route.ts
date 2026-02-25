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
      opa: {
        status: "healthy",
        policy_bundle_version: "2026.02.25.1",
        last_reload_at: "2026-02-25T17:40:00Z",
      },
      vault: {
        status: "healthy",
        transit_key: "spectrastrike-orchestrator-signing",
        latest_version: 3,
      },
    },
    { status: 200 }
  );
}
