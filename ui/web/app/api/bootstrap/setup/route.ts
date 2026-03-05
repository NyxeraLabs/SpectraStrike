/*
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
*/

import { validateAuthenticatedRequest } from "../../../lib/auth-store";
import { applyBootstrapSetup, getBootstrapState } from "../../../lib/bootstrap-store";

type SetupPayload = {
  workspace_name?: string;
  wrappers?: string[];
  federation_endpoint?: string;
};

export async function POST(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json({ error: authDecision.error ?? "unauthorized", legal: authDecision.legal }, { status });
  }

  const payload = (await request.json()) as SetupPayload;
  const wrappers = Array.isArray(payload.wrappers) ? payload.wrappers.map((item) => String(item)) : [];
  applyBootstrapSetup({
    workspaceName: String(payload.workspace_name ?? "default-workspace"),
    wrappers,
    federationEndpoint: String(payload.federation_endpoint ?? "http://localhost:8000"),
  });

  return Response.json({ bootstrap: getBootstrapState(), configured: true }, { status: 200 });
}
