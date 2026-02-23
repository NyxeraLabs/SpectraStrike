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
  enforceRateLimitWithWindow,
  isJsonContentType,
  validateOrigin,
} from "../../../../../lib/request-guards";
import { legalEnforcementService } from "../../../../../lib/legal-enforcement";

type AcceptPayload = {
  accepted_by?: string;
  accepted_documents?: {
    eula?: string;
    aup?: string;
    privacy?: string;
  };
  installation_id?: string;
};

export async function POST(request: Request) {
  const clientKey = `auth-legal-accept:${clientAddressKey(request)}`;
  if (!enforceRateLimitWithWindow(clientKey, 20, 60_000)) {
    return Response.json({ error: "rate_limited" }, { status: 429 });
  }
  if (!validateOrigin(request)) {
    return Response.json({ error: "origin_forbidden" }, { status: 403 });
  }
  if (!isJsonContentType(request)) {
    return Response.json({ error: "unsupported_media_type" }, { status: 415 });
  }

  if (legalEnforcementService.detectEnvironment() !== "self-hosted") {
    return Response.json(
      {
        error: "unsupported_environment",
        message:
          "legal acceptance writes are only handled locally for self-hosted mode",
      },
      { status: 501 }
    );
  }

  try {
    const payload = (await request.json()) as AcceptPayload;
    const acceptedDocuments = payload.accepted_documents ?? {};
    const stored = await legalEnforcementService.recordSelfHostedAcceptance({
      acceptedBy: payload.accepted_by,
      acceptedDocuments,
      installationId: payload.installation_id,
    });
    const decision = await legalEnforcementService.evaluate({
      environment: "self-hosted",
      acceptanceRecord: stored,
    });

    return Response.json(
      {
        status: decision.isCompliant ? "accepted" : "incomplete",
        legal: decision,
        acceptance: stored,
      },
      { status: decision.isCompliant ? 200 : 202 }
    );
  } catch (error) {
    return Response.json(
      {
        error: "legal_acceptance_write_failed",
        message: error instanceof Error ? error.message : "unknown_error",
      },
      { status: 500 }
    );
  }
}
