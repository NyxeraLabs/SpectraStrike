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

import type { WorkflowEdge, WorkflowNode } from "./workflow-graph";

export type PersistedPlaybook = {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  queue: string[];
  updated_at: string;
};

const perTenantPlaybook = new Map<string, PersistedPlaybook>();

export function getPlaybook(tenantId: string): PersistedPlaybook | null {
  return perTenantPlaybook.get(tenantId) ?? null;
}

export function setPlaybook(tenantId: string, value: Omit<PersistedPlaybook, "updated_at">): PersistedPlaybook {
  const payload: PersistedPlaybook = {
    ...value,
    updated_at: new Date().toISOString(),
  };
  perTenantPlaybook.set(tenantId, payload);
  return payload;
}
