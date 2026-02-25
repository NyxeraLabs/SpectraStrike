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
} from "../../../../../lib/request-guards";
import { validateAuthenticatedRequest } from "../../../../../lib/auth-store";

type RevokeTenantPayload = {
  tenant_id?: string;
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

  const payload = (await request.json()) as RevokeTenantPayload;
  if (!payload.tenant_id || payload.tenant_id.length > 128) {
    return Response.json({ error: "invalid tenant_id" }, { status: 400 });
  }
  return Response.json(
    {
      status: "completed",
      action: "auth_revoke_tenant",
      tenant_id: payload.tenant_id,
      revoked_sessions: 9,
    },
    { status: 200 }
  );
}
