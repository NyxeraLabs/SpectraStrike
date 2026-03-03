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
} from "../../../../lib/request-guards";
import { validateAuthenticatedRequest } from "../../../../lib/auth-store";
import { approveArmoryItem } from "../../../../lib/armory-store";
import { authFailureStatus, logApiAudit } from "../../../../lib/observability";

type ApprovePayload = {
  tool_sha256?: string;
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
  const authDecision = await validateAuthenticatedRequest(request, { requiredAnyRole: ["admin", "operator"] });
  if (!authDecision.ok) {
    const status = authFailureStatus(authDecision.error);
    logApiAudit({
      route: "/api/actions/armory/approve",
      action: "armory_approve",
      status,
      actor: authDecision.principal?.userId,
      detail: authDecision.error,
    });
    return Response.json(
      {
        error: authDecision.error ?? "unauthorized",
        legal: authDecision.legal,
      },
      { status }
    );
  }

  const payload = (await request.json()) as ApprovePayload;
  const digest = payload.tool_sha256?.trim() ?? "";
  if (!digest.startsWith("sha256:")) {
    return Response.json({ error: "invalid_tool_sha256" }, { status: 400 });
  }

  const approved = approveArmoryItem(digest, "ui-operator");
  if (!approved) {
    return Response.json({ error: "tool_not_found" }, { status: 404 });
  }
  logApiAudit({
    route: "/api/actions/armory/approve",
    action: "armory_approve",
    status: 200,
    actor: authDecision.principal?.userId,
    detail: digest,
  });

  return Response.json({ status: "approved", item: approved }, { status: 200 });
}
