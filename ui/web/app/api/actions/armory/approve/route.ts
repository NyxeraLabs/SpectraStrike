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

  const payload = (await request.json()) as ApprovePayload;
  const digest = payload.tool_sha256?.trim() ?? "";
  if (!digest.startsWith("sha256:")) {
    return Response.json({ error: "invalid_tool_sha256" }, { status: 400 });
  }

  const approved = approveArmoryItem(digest, "ui-operator");
  if (!approved) {
    return Response.json({ error: "tool_not_found" }, { status: 404 });
  }

  return Response.json({ status: "approved", item: approved }, { status: 200 });
}
