import {
  clientAddressKey,
  enforceRateLimit,
  isJsonContentType,
  validateOrigin,
} from "../../../lib/request-guards";
import { proxyToOrchestrator } from "../../../lib/orchestrator-proxy";

type TaskActionPayload = {
  tool: string;
  target: string;
  parameters?: Record<string, unknown>;
};

function validatePayload(payload: TaskActionPayload): string | null {
  if (!payload.tool || payload.tool.length > 64) {
    return "invalid tool";
  }
  if (!payload.target || payload.target.length > 256) {
    return "invalid target";
  }
  if (payload.parameters && typeof payload.parameters !== "object") {
    return "invalid parameters";
  }
  return null;
}

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

  const payload = (await request.json()) as TaskActionPayload;
  const validationError = validatePayload(payload);
  if (validationError) {
    return Response.json({ error: validationError }, { status: 400 });
  }

  const upstream = await proxyToOrchestrator("/api/v1/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (upstream) {
    const body = await upstream.json();
    return Response.json(body, { status: upstream.status });
  }

  return Response.json(
    {
      task_id: `mock-${Date.now()}`,
      status: "queued",
      mode: "ui-local-fallback",
    },
    { status: 202 }
  );
}
