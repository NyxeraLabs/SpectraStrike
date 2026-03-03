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

"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import {
  buildNexusContext,
  buildVectorVueDeepLink,
  canAccessNexusArea,
  exportUnifiedValidationReport,
  mergeUnifiedActivities,
  searchUnifiedActivities,
  type NexusActivity,
  type NexusContext,
  type NexusRole,
} from "../lib/nexus-context";

type NexusWorkbenchProps = {
  tenantName: string;
  tenantId: string;
  role: NexusRole;
  vectorVueBaseUrl: string;
};

const execFeed: NexusActivity[] = [
  {
    source: "spectrastrike",
    type: "execution",
    title: "Campaign node execution",
    detail: "Privilege escalation branch succeeded for T1068",
    ts: "2026-03-03T13:20:00Z",
  },
  {
    source: "spectrastrike",
    type: "execution",
    title: "Pivot graph update",
    detail: "New lateral movement edge observed on SMB path",
    ts: "2026-03-03T13:18:30Z",
  },
];

const detectionFeed: NexusActivity[] = [
  {
    source: "vectorvue",
    type: "detection",
    title: "Detection event correlated",
    detail: "Alert chain mapped to T1021.002 and queued for analyst review",
    ts: "2026-03-03T13:21:22Z",
  },
  {
    source: "vectorvue",
    type: "assurance",
    title: "Assurance delta",
    detail: "Containment effectiveness increased by 6.2%",
    ts: "2026-03-03T13:17:40Z",
  },
];

function downloadReport(content: string, filename: string): void {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function NexusWorkbench({ tenantName, tenantId, role, vectorVueBaseUrl }: NexusWorkbenchProps) {
  const [campaignId, setCampaignId] = useState("cmp-001");
  const [findingId, setFindingId] = useState("fnd-184");
  const [query, setQuery] = useState("");

  const context: NexusContext = useMemo(
    () =>
      buildNexusContext({
        tenantId,
        tenantName,
        role,
        campaignId,
        findingId,
      }),
    [campaignId, findingId, role, tenantId, tenantName],
  );

  const unifiedFeed = useMemo(() => mergeUnifiedActivities([...execFeed, ...detectionFeed]), []);
  const filteredFeed = useMemo(() => searchUnifiedActivities(unifiedFeed, query), [query, unifiedFeed]);
  const vectorVueLink = useMemo(() => buildVectorVueDeepLink(vectorVueBaseUrl, context), [context, vectorVueBaseUrl]);

  const drilldownHref = `/dashboard/workflow?campaign_id=${encodeURIComponent(campaignId)}&finding_id=${encodeURIComponent(findingId)}`;

  return (
    <section className="grid gap-4">
      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Unified Navigation Shell</h2>
        <p className="mt-2 text-sm text-slate-300">
          Role-aware cross-product routing between SpectraStrike execution and VectorVue detection intelligence.
        </p>
        <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          <Link href="/dashboard/workflow" className="spectra-button-secondary px-3 py-2 text-center text-sm font-semibold">
            SpectraStrike Workflow
          </Link>
          <Link href="/dashboard/asm" className="spectra-button-secondary px-3 py-2 text-center text-sm font-semibold">
            SpectraStrike ASM
          </Link>
          <a href={vectorVueLink} className="spectra-button-primary px-3 py-2 text-center text-sm font-semibold">
            VectorVue Nexus
          </a>
          <Link href="/dashboard/telemetry" className="spectra-button-secondary px-3 py-2 text-center text-sm font-semibold">
            Telemetry Feed
          </Link>
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-info">Shared Authentication & RBAC Layer</h2>
        <p className="mt-2 text-sm text-slate-300">
          Active role <span className="spectra-mono text-white">{role}</span> governs cross-product areas.
        </p>
        <ul className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
          <li>Execution: {canAccessNexusArea(role, "execution") ? "allowed" : "restricted"}</li>
          <li>Detection: {canAccessNexusArea(role, "detection") ? "allowed" : "restricted"}</li>
          <li>Assurance: {canAccessNexusArea(role, "assurance") ? "allowed" : "restricted"}</li>
          <li>Export: {canAccessNexusArea(role, "export") ? "allowed" : "restricted"}</li>
        </ul>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-warning">Unified Activity Feed</h2>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search execution, detection, assurance"
          className="mt-3 w-full rounded border border-borderSubtle bg-slate-950/80 px-3 py-2 text-sm text-white"
        />
        <ol className="mt-3 space-y-2" data-testid="nexus-feed">
          {filteredFeed.map((item) => (
            <li key={`${item.source}-${item.ts}-${item.title}`} className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2 text-sm">
              <span className="spectra-mono text-slate-400">[{item.source}/{item.type}]</span> {item.title}
              <p className="mt-1 text-xs text-slate-300">{item.detail}</p>
            </li>
          ))}
        </ol>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-success">Campaign → Detection → Assurance Drill-Down</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-3">
          <label className="text-sm text-slate-300">
            Campaign ID
            <input
              value={campaignId}
              onChange={(event) => setCampaignId(event.target.value)}
              className="mt-1 w-full rounded border border-borderSubtle bg-slate-950/80 px-2 py-2 text-sm text-white"
            />
          </label>
          <label className="text-sm text-slate-300">
            Detection Finding ID
            <input
              value={findingId}
              onChange={(event) => setFindingId(event.target.value)}
              className="mt-1 w-full rounded border border-borderSubtle bg-slate-950/80 px-2 py-2 text-sm text-white"
            />
          </label>
          <div className="flex items-end">
            <Link href={drilldownHref} className="spectra-button-primary w-full px-3 py-2 text-center text-sm font-semibold">
              Open SpectraStrike Drill-Down
            </Link>
          </div>
        </div>
      </article>

      {canAccessNexusArea(role, "export") ? (
        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Export Unified Validation Report</h2>
          <button
            type="button"
            className="spectra-button-primary mt-3 px-4 py-2 text-sm font-semibold"
            onClick={() =>
              downloadReport(
                exportUnifiedValidationReport(context, filteredFeed),
                `nexus-validation-${context.tenantId}-${new Date().toISOString().slice(0, 10)}.md`,
              )
            }
          >
            Export Report
          </button>
        </article>
      ) : null}
    </section>
  );
}
