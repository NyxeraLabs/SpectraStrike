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

export type ExecutionTaskItem = {
  task_id?: string;
  tool?: string;
  target?: string;
  status?: string;
  retry_count?: number;
  created_at?: string;
  updated_at?: string;
};

export type TelemetryEventItem = {
  event_id?: string;
  source?: string;
  status?: string;
  event_type?: string;
  actor?: string;
  target?: string;
  timestamp?: string;
  envelope_id?: string;
  signature_state?: string;
  attestation_proof?: string;
  retry_attempts?: number;
  failure_reason?: string;
  vectorvue_response?: string;
};

export type FederationDiagnostic = {
  envelopeId: string;
  signatureState: string;
  failureReason: string;
  retryAttempts: number;
  vectorVueResponse: string;
  attestationProof: string;
  timestamp: string;
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

export function buildExecutionActivities(items: ExecutionTaskItem[]): NexusActivity[] {
  return items.map((item) => {
    const tool = clean(item.tool ?? "unknown-tool");
    const target = clean(item.target ?? "unknown-target");
    const status = clean(item.status ?? "queued");
    const retryCount = Number(item.retry_count ?? 0);
    return {
      source: "spectrastrike",
      type: "execution",
      title: `Execution task ${tool}`,
      detail: `${status} on ${target} (retries=${retryCount})`,
      ts: item.updated_at ?? item.created_at ?? new Date().toISOString(),
    };
  });
}

export function buildTelemetryActivities(items: TelemetryEventItem[]): NexusActivity[] {
  return items.map((item) => {
    const eventType = clean(item.event_type ?? "telemetry_event");
    const target = clean(item.target ?? "unknown-target");
    const status = clean(item.status ?? "unknown");
    const hasAssuranceSignals = Boolean(item.vectorvue_response || item.signature_state || item.attestation_proof);
    const type: NexusActivity["type"] = hasAssuranceSignals ? "assurance" : "detection";
    return {
      source: hasAssuranceSignals ? "vectorvue" : "spectrastrike",
      type,
      title: `Telemetry ${eventType}`,
      detail: `${status} on ${target}`,
      ts: item.timestamp ?? new Date().toISOString(),
    };
  });
}

export function buildFederationDiagnostics(items: TelemetryEventItem[]): FederationDiagnostic[] {
  return items
    .filter((item) =>
      Boolean(item.envelope_id || item.signature_state || item.failure_reason || item.vectorvue_response || item.attestation_proof),
    )
    .map((item) => ({
      envelopeId: clean(item.envelope_id ?? "n/a"),
      signatureState: clean(item.signature_state ?? "n/a"),
      failureReason: clean(item.failure_reason ?? "none"),
      retryAttempts: Number(item.retry_attempts ?? 0),
      vectorVueResponse: clean(item.vectorvue_response ?? "n/a"),
      attestationProof: clean(item.attestation_proof ?? "n/a"),
      timestamp: item.timestamp ?? new Date().toISOString(),
    }));
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
