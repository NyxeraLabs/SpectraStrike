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

import React, { useEffect, useMemo, useState } from "react";

import {
  defaultAsmGraph,
  edgeCountsByRelation,
  exposureGraphToPlaybookActions,
  reorderAsmNodes,
  riskOverlayByAsset,
  type AsmNode,
} from "../lib/asm-graph";

const palette: AsmNode[] = [
  { id: "p-cdn", label: "CDN Endpoint", nodeType: "external", riskScore: 0.52 },
  { id: "p-k8s", label: "K8s Service", nodeType: "service", riskScore: 0.58 },
  { id: "p-ad", label: "AD Tier", nodeType: "internal", riskScore: 0.66 },
  { id: "p-role", label: "Cloud Role", nodeType: "cloud_identity", riskScore: 0.71 },
];

function riskClass(level: "low" | "medium" | "high" | "critical"): string {
  if (level === "critical") return "ring-critical bg-critical/15";
  if (level === "high") return "ring-warning bg-warning/15";
  if (level === "medium") return "ring-info bg-info/15";
  return "ring-success bg-success/15";
}

function typeClass(type: AsmNode["nodeType"]): string {
  if (type === "external") return "text-critical";
  if (type === "service") return "text-telemetryGlow";
  if (type === "internal") return "text-warning";
  return "text-info";
}

type AsmWorkbenchProps = {
  initialNodes?: AsmNode[];
};

export function AsmWorkbench({ initialNodes }: AsmWorkbenchProps) {
  const graph = useMemo(() => defaultAsmGraph(), []);
  const [nodes, setNodes] = useState<AsmNode[]>(initialNodes ?? graph.nodes);
  const [edges, setEdges] = useState(graph.edges);
  const [exposures, setExposures] = useState(graph.exposures);
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [selectedAssetId, setSelectedAssetId] = useState<string>(graph.nodes[0]?.id ?? "");
  const [campaignTimeline, setCampaignTimeline] = useState<string[]>([]);
  const [asmStatus, setAsmStatus] = useState<string>("Loading live campaign graph surfaces...");
  const [asmFullscreen, setAsmFullscreen] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch("/ui/api/execution/queue?limit=50", { cache: "no-store" }).then((res) => res.json()),
      fetch("/ui/api/telemetry/events?limit=50", { cache: "no-store" }).then((res) => res.json()),
    ])
      .then(([queueBody, telemetryBody]) => {
        if (!active) return;
        const queueItems = Array.isArray(queueBody.items) ? queueBody.items : [];
        const telemetryItems = Array.isArray(telemetryBody.items) ? telemetryBody.items : [];
        if (queueItems.length === 0 && telemetryItems.length === 0) {
          setAsmStatus("Using local ASM graph dataset.");
          return;
        }

        const liveNodes: AsmNode[] = queueItems.map((item: Record<string, unknown>, idx: number) => {
          const status = String(item.status ?? "queued");
          const riskScore = status === "failed" ? 0.92 : status === "retrying" ? 0.78 : status === "running" ? 0.66 : 0.53;
          const label = String(item.tool ?? `task-${idx + 1}`);
          return {
            id: `live-${idx}-${label}`,
            label,
            nodeType: idx % 4 === 0 ? "external" : idx % 4 === 1 ? "service" : idx % 4 === 2 ? "internal" : "cloud_identity",
            riskScore,
          };
        });

        if (liveNodes.length > 1) {
          setNodes(liveNodes);
          setSelectedAssetId(liveNodes[0].id);
          setEdges(
            liveNodes.slice(1).map((node, idx) => ({
              id: `live-edge-${idx}`,
              sourceId: liveNodes[idx].id,
              targetId: node.id,
              relation: idx % 3 === 0 ? "pivot" : idx % 2 === 0 ? "vuln_path" : "exposes",
            })),
          );
        }

        if (telemetryItems.length > 0 && liveNodes.length > 0) {
          setExposures(
            telemetryItems.slice(0, 20).map((item: Record<string, unknown>, idx: number) => ({
              assetId: liveNodes[idx % liveNodes.length].id,
              exposureId: String(item.event_id ?? `evt-${idx}`),
              severity: String(item.status ?? "info").toLowerCase() === "failed" ? 0.9 : 0.62,
              technique: String(item.event_type ?? "T0000"),
            })),
          );
        }

        setCampaignTimeline(
          [...queueItems, ...telemetryItems]
            .slice(0, 12)
            .map((item: Record<string, unknown>) => `${String(item.timestamp ?? item.updated_at ?? new Date().toISOString())} :: ${String(item.tool ?? item.event_type ?? item.source ?? "event")} :: ${String(item.status ?? "unknown")}`),
        );
        setAsmStatus("Live campaign graph surfaces loaded.");
      })
      .catch(() => {
        if (!active) return;
        setAsmStatus("Unable to load live campaign graph surfaces; using local dataset.");
      });
    return () => {
      active = false;
    };
  }, []);

  const overlays = useMemo(() => riskOverlayByAsset(nodes), [nodes]);
  const relationCounts = useMemo(() => edgeCountsByRelation(edges), [edges]);
  const playbookActions = useMemo(() => exposureGraphToPlaybookActions(exposures), [exposures]);
  const externalPivotPath = useMemo(
    () => edges.filter((edge) => edge.relation === "pivot" || edge.relation === "exposes"),
    [edges],
  );

  const selectedExposures = exposures.filter((row) => row.assetId === selectedAssetId);

  return (
    <section className="grid gap-4 xl:grid-cols-[1.1fr_1fr]">
      <article className="spectra-panel p-5">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Asset Graph Visualization Engine</h2>
          <button
            type="button"
            className="spectra-button-secondary px-3 py-1.5 text-xs"
            onClick={() => setAsmFullscreen((current) => !current)}
          >
            {asmFullscreen ? "Exit Full Screen" : "Full Screen"}
          </button>
        </div>
        <p className="mt-2 text-xs text-slate-400">{asmStatus}</p>
        <div className={`relative mt-4 rounded-lg border border-borderSubtle bg-slate-950/70 p-2 ${asmFullscreen ? "fixed inset-4 z-50 h-[calc(100vh-2rem)]" : ""}`}>
        <svg viewBox="0 0 760 280" className={`w-full rounded-lg bg-slate-950/70 p-2 ${asmFullscreen ? "h-[calc(100vh-6rem)]" : ""}`}>
          {nodes.slice(0, 7).map((node, idx) => {
            const x = 90 + (idx % 4) * 170;
            const y = 80 + Math.floor(idx / 4) * 130;
            return (
              <g key={node.id} data-testid={`asm-node-${node.id}`}>
                <circle cx={x} cy={y} r={26} fill="#1a2238" stroke="#8ba6ff" />
                <text x={x} y={y + 3} fill="#e6e9f5" textAnchor="middle" fontSize="9">
                  {node.label.slice(0, 8)}
                </text>
              </g>
            );
          })}
          {externalPivotPath.slice(0, 6).map((edge, idx) => {
            const x1 = 90 + (idx % 4) * 170;
            const y1 = 80 + Math.floor(idx / 4) * 130;
            const x2 = 90 + ((idx + 1) % 4) * 170;
            const y2 = 80 + Math.floor((idx + 1) / 4) * 130;
            return <line key={edge.id} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#22c55e" strokeWidth="2" />;
          })}
        </svg>
        {asmFullscreen ? (
          <button
            type="button"
            className="spectra-button-secondary absolute right-4 top-4 z-10 px-3 py-1.5 text-xs"
            onClick={() => setAsmFullscreen(false)}
          >
            Close
          </button>
        ) : null}
        </div>
      </article>

      <article className="spectra-panel p-5" data-testid="asm-builder">
        <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Drag-and-Drop Asset Relationship Builder</h2>
        <div className="mt-3 rounded-lg border border-borderSubtle bg-slate-950/70 p-3">
          <p className="text-xs uppercase tracking-wide text-slate-400">Asset Palette</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {palette.map((asset) => (
              <button
                key={asset.id}
                type="button"
                className="spectra-button-secondary px-2 py-1 text-xs font-semibold"
                onClick={() => setNodes((prev) => [...prev, { ...asset, id: `asm-${Date.now()}-${asset.id}` }])}
              >
                + {asset.label}
              </button>
            ))}
          </div>
        </div>
        <ul className="mt-3 space-y-2">
          {nodes.map((node) => (
            <li
              key={node.id}
              draggable
              onDragStart={() => setDraggedId(node.id)}
              onDragOver={(event) => event.preventDefault()}
              onDrop={() => {
                if (!draggedId) return;
                setNodes((prev) => reorderAsmNodes(prev, draggedId, node.id));
                setDraggedId(null);
              }}
              className={`cursor-move rounded border border-borderSubtle px-2 py-2 text-sm ring-1 ${riskClass(overlays[node.id])}`}
              data-testid={`asm-list-${node.id}`}
            >
              <span className={`spectra-mono ${typeClass(node.nodeType)}`}>{node.nodeType}</span> {node.label}
            </li>
          ))}
        </ul>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-warning">Exposure-to-Asset Linking Visualization</h2>
        <select
          value={selectedAssetId}
          onChange={(event) => setSelectedAssetId(event.target.value)}
          className="mt-3 w-full rounded border border-borderSubtle bg-slate-950/80 px-2 py-2 text-sm"
          data-testid="asset-selector"
        >
          {nodes.map((node) => (
            <option key={node.id} value={node.id}>
              {node.label}
            </option>
          ))}
        </select>
        <div className="mt-3 space-y-2" data-testid="exposure-links">
          {selectedExposures.length > 0 ? (
            selectedExposures.map((row) => (
              <div key={row.exposureId} className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2 text-sm">
                {row.exposureId} mapped to {row.technique} ({Math.round(row.severity * 100)}%)
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-300">No mapped exposures for selected asset.</p>
          )}
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-critical">Vulnerability Relationship Mapping</h2>
        <p className="mt-3 text-sm text-slate-200">Vulnerability-path edges: {relationCounts.vuln_path}</p>
        <p className="mt-1 text-sm text-slate-200">Exposed surface edges: {relationCounts.exposes}</p>
      </article>

      <article className="spectra-panel p-5" data-testid="pivot-panel">
        <h2 className="text-sm uppercase tracking-[0.2em] text-info">External-to-Internal Pivot Path Visualization</h2>
        <ol className="mt-3 space-y-2 text-sm">
          {externalPivotPath.map((edge) => (
            <li key={edge.id} className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2">
              {edge.sourceId} → {edge.targetId} ({edge.relation})
            </li>
          ))}
        </ol>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-success">Cloud IAM &amp; Role Relationship Graph</h2>
        <ul className="mt-3 space-y-2 text-sm">
          {edges
            .filter((edge) => edge.relation === "iam_assume_role")
            .map((edge) => (
              <li key={edge.id} className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2">
                {edge.sourceId} assumes {edge.targetId}
              </li>
            ))}
        </ul>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-warning">Exposure Risk Overlay Scoring Visualization</h2>
        <div className="mt-3 grid gap-2">
          {nodes.map((node) => (
            <div key={`risk-${node.id}`} className="rounded border border-borderSubtle bg-slate-950/70 p-3 text-sm">
              <p>{node.label}</p>
              <div className="mt-2 h-2 w-full rounded bg-slate-800">
                <div className="h-2 rounded bg-warning" style={{ width: `${Math.round(node.riskScore * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      </article>

      <article className="spectra-panel p-5" data-testid="playbook-convert">
        <h2 className="text-sm uppercase tracking-[0.2em] text-telemetryGlow">
          Convert Exposure Graph to SpectraStrike Playbook Action
        </h2>
        <ol className="mt-3 space-y-2 text-sm">
          {playbookActions.map((line) => (
            <li key={line} className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2">
              {line}
            </li>
          ))}
        </ol>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Campaign Timeline</h2>
        <ol className="mt-3 space-y-2 text-sm" data-testid="campaign-timeline">
          {campaignTimeline.length > 0 ? (
            campaignTimeline.map((line) => (
              <li key={line} className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2">
                {line}
              </li>
            ))
          ) : (
            <li className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2 text-slate-300">
              No live campaign events yet.
            </li>
          )}
        </ol>
      </article>
    </section>
  );
}
