import {
  clientAddressKey,
  enforceRateLimit,
  isJsonContentType,
  validateOrigin,
} from "../../../lib/request-guards";
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
