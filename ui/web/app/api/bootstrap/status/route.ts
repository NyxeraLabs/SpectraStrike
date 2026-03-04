/*
Copyright (c) 2026 NyxeraLabs
Licensed under BSL 1.1
*/

import { getAuthStoreStats, validateAuthenticatedRequest } from "../../../lib/auth-store";
import { getBootstrapState, getBootstrapZeroStatus } from "../../../lib/bootstrap-store";

export async function GET(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json({ error: authDecision.error ?? "unauthorized", legal: authDecision.legal }, { status });
  }

  const authStats = getAuthStoreStats();
  return Response.json(
    {
      status: getBootstrapZeroStatus(authStats.users),
      bootstrap: getBootstrapState(),
    },
    { status: 200, headers: { "cache-control": "no-store" } },
  );
}
