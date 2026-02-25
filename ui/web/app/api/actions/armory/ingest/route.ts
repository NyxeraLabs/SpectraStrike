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

type ArmoryIngestPayload = {
  tool_name?: string;
  image_ref?: string;
  mode?: "dry_run" | "ingest";
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

  const payload = (await request.json()) as ArmoryIngestPayload;
  return Response.json(
    {
      status: "accepted",
      mode: payload.mode ?? "dry_run",
      tool_name: payload.tool_name ?? "unknown-tool",
      image_ref: payload.image_ref ?? "registry.local/unknown:latest",
      sbom_status: "queued",
      vuln_scan_status: "queued",
      signature_status: "pending_approval",
    },
    { status: 202 }
  );
}
