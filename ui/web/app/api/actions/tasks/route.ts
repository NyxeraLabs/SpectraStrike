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
import { validateAuthenticatedRequest } from "../../../lib/auth-store";
import { proxyToOrchestrator } from "../../../lib/orchestrator-proxy";

type TaskActionPayload = {
  tool: string;
  target: string;
  parameters?: Record<string, unknown>;
  tenant_id?: string;
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
  if (payload.tenant_id && !/^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$/.test(payload.tenant_id)) {
    return "invalid tenant_id";
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

  const payload = (await request.json()) as TaskActionPayload;
  const tenantId = payload.tenant_id ?? process.env.SPECTRASTRIKE_TENANT_ID ?? "";
  const normalizedPayload: TaskActionPayload = {
    ...payload,
    tenant_id: tenantId,
  };
  const validationError = validatePayload(normalizedPayload);
  if (validationError) {
    return Response.json({ error: validationError }, { status: 400 });
  }
  if (!tenantId) {
    return Response.json({ error: "tenant_id_required" }, { status: 400 });
  }

  const upstream = await proxyToOrchestrator("/api/v1/tasks", {
    method: "POST",
    body: JSON.stringify(normalizedPayload),
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
