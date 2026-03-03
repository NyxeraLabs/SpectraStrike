/*
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
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

import { validateAuthenticatedRequest } from "../../../lib/auth-store";
import { clearPlaybooks } from "../../../lib/execution-playbook-store";
import { clearRuntimeTasks } from "../../../lib/execution-runtime-store";

export async function POST(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json(
      {
        error: authDecision.error ?? "unauthorized",
        legal: authDecision.legal,
      },
      { status },
    );
  }

  const clearedTasks = clearRuntimeTasks();
  const clearedPlaybooks = clearPlaybooks();
  return Response.json(
    {
      cleared_tasks: clearedTasks,
      cleared_playbooks: clearedPlaybooks,
      mode: "ui-local-store-reset",
    },
    { status: 200, headers: { "cache-control": "no-store" } },
  );
}
