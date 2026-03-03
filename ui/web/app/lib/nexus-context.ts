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

export type NexusRole = "operator" | "analyst" | "auditor" | "admin";
export type NexusArea = "execution" | "detection" | "assurance" | "export";

export type NexusContext = {
  v: "1";
  tenantId: string;
  tenantName: string;
  role: NexusRole;
  campaignId?: string;
  findingId?: string;
  ts: string;
};

export type NexusActivity = {
  source: "spectrastrike" | "vectorvue";
  type: "execution" | "detection" | "assurance";
  title: string;
  detail: string;
  ts: string;
};

const rolePermissions: Record<NexusRole, NexusArea[]> = {
  operator: ["execution", "detection"],
  analyst: ["detection", "assurance"],
  auditor: ["assurance", "export"],
  admin: ["execution", "detection", "assurance", "export"],
};

function clean(value: string): string {
  return value.trim();
}

export function canAccessNexusArea(role: NexusRole, area: NexusArea): boolean {
  return rolePermissions[role].includes(area);
}

export function buildNexusContext(input: Omit<NexusContext, "v" | "ts"> & { ts?: string }): NexusContext {
  return {
    v: "1",
    tenantId: clean(input.tenantId),
    tenantName: clean(input.tenantName),
    role: input.role,
    campaignId: input.campaignId ? clean(input.campaignId) : undefined,
    findingId: input.findingId ? clean(input.findingId) : undefined,
    ts: input.ts ?? new Date().toISOString(),
  };
}

export function encodeNexusContext(context: NexusContext): string {
  const params = new URLSearchParams();
  params.set("nexus_v", context.v);
  params.set("tenant_id", context.tenantId);
  params.set("tenant_name", context.tenantName);
  params.set("role", context.role);
  params.set("ts", context.ts);
  if (context.campaignId) params.set("campaign_id", context.campaignId);
  if (context.findingId) params.set("finding_id", context.findingId);
  return params.toString();
}

export function decodeNexusContext(search: string): NexusContext | null {
  const raw = search.startsWith("?") ? search.slice(1) : search;
  const params = new URLSearchParams(raw);
  const v = params.get("nexus_v");
  const tenantId = params.get("tenant_id")?.trim() ?? "";
  const tenantName = params.get("tenant_name")?.trim() ?? "";
  const role = (params.get("role")?.trim() ?? "") as NexusRole;
  const ts = params.get("ts")?.trim() ?? "";

  if (v !== "1") return null;
  if (!tenantId || !tenantName || !ts) return null;
  if (!(role in rolePermissions)) return null;

  const campaignId = params.get("campaign_id")?.trim() ?? undefined;
  const findingId = params.get("finding_id")?.trim() ?? undefined;

  return {
    v: "1",
    tenantId,
    tenantName,
    role,
    campaignId: campaignId || undefined,
    findingId: findingId || undefined,
    ts,
  };
}

function joinUrl(base: string, path: string): string {
  const left = base.replace(/\/$/, "");
  const right = path.startsWith("/") ? path : `/${path}`;
  return `${left}${right}`;
}

export function buildVectorVueDeepLink(baseUrl: string, context: NexusContext): string {
  return `${joinUrl(baseUrl, "/portal/nexus")}?${encodeNexusContext(context)}`;
}

export function buildSpectraStrikeDeepLink(baseUrl: string, context: NexusContext): string {
  return `${joinUrl(baseUrl, "/ui/dashboard/nexus")}?${encodeNexusContext(context)}`;
}

export function mergeUnifiedActivities(items: NexusActivity[]): NexusActivity[] {
  return [...items].sort((a, b) => Date.parse(b.ts) - Date.parse(a.ts));
}

export function searchUnifiedActivities(items: NexusActivity[], query: string): NexusActivity[] {
  const q = query.trim().toLowerCase();
  if (!q) return items;
  return items.filter((item) => `${item.title} ${item.detail} ${item.type} ${item.source}`.toLowerCase().includes(q));
}

export function exportUnifiedValidationReport(context: NexusContext, activities: NexusActivity[]): string {
  const lines = [
    "# Unified Validation Report",
    "",
    `- Tenant: ${context.tenantName} (${context.tenantId})`,
    `- Role: ${context.role}`,
    `- Campaign: ${context.campaignId ?? "n/a"}`,
    `- Finding: ${context.findingId ?? "n/a"}`,
    `- Generated: ${new Date().toISOString()}`,
    "",
    "## Unified Activity Feed",
  ];

  activities.forEach((item) => {
    lines.push(`- [${item.source}/${item.type}] ${item.ts} :: ${item.title} :: ${item.detail}`);
  });

  return lines.join("\n");
}
