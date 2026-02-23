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

import {
  clientAddressKey,
  enforceRateLimit,
  isJsonContentType,
  validateOrigin,
} from "../../../lib/request-guards";
import { isAuthenticatedRequest } from "../../../lib/auth-store";
import { proxyToOrchestrator } from "../../../lib/orchestrator-proxy";

type ManualSyncPayload = {
  actor?: string;
  checkpoint_override?: string;
};

export async function POST(request: Request) {
  if (!enforceRateLimit(clientAddressKey(request))) {
    return Response.json({ error: "rate_limited" }, { status: 429 });
  }
  if (!validateOrigin(request)) {
    return Response.json({ error: "origin_forbidden" }, { status: 403 });
  }
  if (!isJsonContentType(request)) {
    return Response.json({ error: "unsupported_media_type" }, { status: 415 });
  }
  if (!(await isAuthenticatedRequest(request))) {
    return Response.json({ error: "unauthorized" }, { status: 401 });
  }

  const payload = (await request.json()) as ManualSyncPayload;
  if (payload.actor && payload.actor.length > 96) {
    return Response.json({ error: "invalid actor" }, { status: 400 });
  }

  const upstream = await proxyToOrchestrator("/api/v1/integrations/metasploit/manual-sync", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (upstream) {
    const body = await upstream.json();
    return Response.json(body, { status: upstream.status });
  }

  return Response.json(
    {
      emitted_events: 3,
      observed_sessions: 1,
      observed_session_events: 4,
      mode: "ui-local-fallback",
    },
    { status: 200 }
  );
}
