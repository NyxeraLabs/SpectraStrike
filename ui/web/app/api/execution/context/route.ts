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

type CampaignOption = {
  id: string;
  label: string;
};

type TenantOption = {
  id: string;
  label: string;
  campaigns: CampaignOption[];
};

const defaultTenants: TenantOption[] = [
  {
    id: "10000000-0000-0000-0000-000000000001",
    label: "ACME Industries",
    campaigns: [
      { id: "OP_ACME_REDWOLF_2026", label: "OP_ACME_REDWOLF_2026" },
      { id: "OP_ACME_NIGHTGLASS_2026", label: "OP_ACME_NIGHTGLASS_2026" },
    ],
  },
  {
    id: "20000000-0000-0000-0000-000000000002",
    label: "Globex Corporation",
    campaigns: [
      { id: "OP_GLOBEX_REDWOLF_2026", label: "OP_GLOBEX_REDWOLF_2026" },
      { id: "OP_GLOBEX_NIGHTGLASS_2026", label: "OP_GLOBEX_NIGHTGLASS_2026" },
    ],
  },
];

function parseTenantCatalog(): TenantOption[] {
  const raw = process.env.SPECTRASTRIKE_TENANT_CAMPAIGNS_JSON?.trim() ?? "";
  if (!raw) return defaultTenants;
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return defaultTenants;
    const tenants: TenantOption[] = [];
    for (const tenant of parsed) {
      if (typeof tenant !== "object" || tenant === null) continue;
      const id = String((tenant as { id?: unknown }).id ?? "").trim();
      const label = String((tenant as { label?: unknown }).label ?? id).trim();
      const campaignsRaw = (tenant as { campaigns?: unknown }).campaigns;
      if (!id || !Array.isArray(campaignsRaw)) continue;
      const campaigns: CampaignOption[] = campaignsRaw
        .filter((item): item is { id?: unknown; label?: unknown } => typeof item === "object" && item !== null)
        .map((item) => ({
          id: String(item.id ?? "").trim(),
          label: String(item.label ?? item.id ?? "").trim(),
        }))
        .filter((item) => item.id.length > 0 && item.label.length > 0);
      if (campaigns.length === 0) continue;
      tenants.push({ id, label: label || id, campaigns });
    }
    return tenants.length > 0 ? tenants : defaultTenants;
  } catch {
    return defaultTenants;
  }
}

function parseRoleTenantMap(): Record<string, string[]> {
  const raw = process.env.SPECTRASTRIKE_ROLE_TENANT_MAP?.trim() ?? "";
  const out: Record<string, string[]> = {};
  if (!raw) return out;
  for (const chunk of raw.split(",")) {
    const [roleRaw, tenantIdsRaw] = chunk.split(":");
    const role = (roleRaw ?? "").trim().toLowerCase();
    const tenantIds = (tenantIdsRaw ?? "")
      .split("|")
      .map((value) => value.trim())
      .filter(Boolean);
    if (!role || tenantIds.length === 0) continue;
    out[role] = tenantIds;
  }
  return out;
}

function resolveVisibleTenants(roles: string[], catalog: TenantOption[]): TenantOption[] {
  const loweredRoles = roles.map((role) => role.toLowerCase());
  if (loweredRoles.includes("admin")) {
    return catalog;
  }
  const roleTenantMap = parseRoleTenantMap();
  const allowedTenantIds = new Set<string>();
  for (const role of loweredRoles) {
    for (const tenantId of roleTenantMap[role] ?? []) {
      allowedTenantIds.add(tenantId);
    }
  }
  if (allowedTenantIds.size === 0) {
    return catalog.slice(0, 1);
  }
  const filtered = catalog.filter((tenant) => allowedTenantIds.has(tenant.id));
  return filtered.length > 0 ? filtered : catalog.slice(0, 1);
}

export async function GET(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json({ error: authDecision.error ?? "unauthorized", legal: authDecision.legal }, { status });
  }

  const catalog = parseTenantCatalog();
  const visibleTenants = resolveVisibleTenants(authDecision.principal?.roles ?? [], catalog);
  return Response.json(
    {
      tenants: visibleTenants,
      scope: visibleTenants.length === 1 ? "single" : visibleTenants.length === catalog.length ? "all" : "restricted",
    },
    { status: 200, headers: { "cache-control": "no-store" } },
  );
}
