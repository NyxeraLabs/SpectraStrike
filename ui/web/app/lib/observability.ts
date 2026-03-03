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

type ApiAudit = {
  route: string;
  action: string;
  status: number;
  actor?: string;
  detail?: string;
};

export function authFailureStatus(error?: "unauthorized" | "forbidden" | "LEGAL_ACCEPTANCE_REQUIRED"): number {
  if (error === "forbidden" || error === "LEGAL_ACCEPTANCE_REQUIRED") return 403;
  return 401;
}

export function logApiAudit(event: ApiAudit): void {
  const payload = {
    ts: new Date().toISOString(),
    route: event.route,
    action: event.action,
    status: event.status,
    actor: event.actor ?? "unknown",
    detail: event.detail ?? "",
  };
  // Structured audit line for integration with log shippers.
  console.info("[spectrastrike-api-audit]", JSON.stringify(payload));
}
