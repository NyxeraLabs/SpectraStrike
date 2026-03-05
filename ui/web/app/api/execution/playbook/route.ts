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
import { getPlaybook, setPlaybook } from "../../../lib/execution-playbook-store";
import { defaultWorkflowGraph, type WorkflowEdge, type WorkflowNode } from "../../../lib/workflow-graph";
import { proxyToOrchestrator } from "../../../lib/orchestrator-proxy";

type PlaybookPayload = {
  tenant_id?: string;
  campaign_id?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  queue: string[];
};

function resolveTenantId(request: Request, payloadTenant?: string): string {
  return payloadTenant ?? process.env.SPECTRASTRIKE_TENANT_ID ?? "tenant-a";
}

function resolveCampaignId(payloadCampaign?: string): string {
  return payloadCampaign ?? "default-campaign";
}

function playbookScopeKey(tenantId: string, campaignId: string): string {
  return `${tenantId}::${campaignId}`;
}

export async function GET(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json({ error: authDecision.error ?? "unauthorized", legal: authDecision.legal }, { status });
  }

  const url = new URL(request.url);
  const tenantId = resolveTenantId(request, url.searchParams.get("tenant_id") ?? undefined);
  const campaignId = resolveCampaignId(url.searchParams.get("campaign_id") ?? undefined);
  const upstream = await proxyToOrchestrator(
    `/api/v1/execution/playbook?tenant_id=${encodeURIComponent(tenantId)}&campaign_id=${encodeURIComponent(campaignId)}`,
    { method: "GET" },
  );
  if (upstream && upstream.ok) {
    const body = await upstream.json();
    return Response.json(body, { status: 200, headers: { "cache-control": "no-store" } });
  }

  const local = getPlaybook(playbookScopeKey(tenantId, campaignId));
  if (local) {
    return Response.json({ tenant_id: tenantId, campaign_id: campaignId, ...local, source: "ui_local_store" }, { status: 200 });
  }
  const fallback = defaultWorkflowGraph();
  return Response.json(
    {
      tenant_id: tenantId,
      campaign_id: campaignId,
      nodes: fallback.nodes,
      edges: fallback.edges,
      queue: [],
      source: "ui_local_store",
      updated_at: new Date(0).toISOString(),
    },
    { status: 200 }
  );
}

export async function PUT(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json({ error: authDecision.error ?? "unauthorized", legal: authDecision.legal }, { status });
  }

  const payload = (await request.json()) as PlaybookPayload;
  const tenantId = resolveTenantId(request, payload.tenant_id);
  const campaignId = resolveCampaignId(payload.campaign_id);
  if (!Array.isArray(payload.nodes) || !Array.isArray(payload.edges) || !Array.isArray(payload.queue)) {
    return Response.json({ error: "invalid_playbook_payload" }, { status: 400 });
  }

  const upstream = await proxyToOrchestrator("/api/v1/execution/playbook", {
    method: "PUT",
    body: JSON.stringify({
      tenant_id: tenantId,
      campaign_id: campaignId,
      nodes: payload.nodes,
      edges: payload.edges,
      queue: payload.queue,
    }),
  });
  if (upstream && upstream.ok) {
    const body = await upstream.json();
    return Response.json(body, { status: 200, headers: { "cache-control": "no-store" } });
  }

  const persisted = setPlaybook(playbookScopeKey(tenantId, campaignId), {
    nodes: payload.nodes,
    edges: payload.edges,
    queue: payload.queue,
  });
  return Response.json({ tenant_id: tenantId, campaign_id: campaignId, ...persisted, source: "ui_local_store" }, { status: 200 });
}
