/*
Copyright (c) 2026 NyxeraLabs
Licensed under BSL 1.1
*/

import { resetAuthStore, validateAuthenticatedRequest } from "../../../lib/auth-store";
import { resetBootstrapState } from "../../../lib/bootstrap-store";
import { clearPlaybooks } from "../../../lib/execution-playbook-store";
import { clearRuntimeTasks } from "../../../lib/execution-runtime-store";

export async function POST(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json({ error: authDecision.error ?? "unauthorized", legal: authDecision.legal }, { status });
  }

  const url = new URL(request.url);
  const wipeAuth = url.searchParams.get("wipe_auth") === "true";
  const clearedTasks = clearRuntimeTasks();
  const clearedPlaybooks = clearPlaybooks();
  const bootstrapBefore = resetBootstrapState();
  const authBefore = wipeAuth ? resetAuthStore() : null;

  return Response.json(
    {
      cleared_tasks: clearedTasks,
      cleared_playbooks: clearedPlaybooks,
      bootstrap_before: bootstrapBefore,
      auth_before: authBefore,
      mode: "first_run_reset",
    },
    { status: 200, headers: { "cache-control": "no-store" } },
  );
}
