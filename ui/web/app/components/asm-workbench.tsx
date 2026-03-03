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

import React, { useMemo, useState } from "react";

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
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [selectedAssetId, setSelectedAssetId] = useState<string>(graph.nodes[0]?.id ?? "");

  const overlays = useMemo(() => riskOverlayByAsset(nodes), [nodes]);
  const relationCounts = useMemo(() => edgeCountsByRelation(graph.edges), [graph.edges]);
  const playbookActions = useMemo(() => exposureGraphToPlaybookActions(graph.exposures), [graph.exposures]);
  const externalPivotPath = useMemo(
    () => graph.edges.filter((edge) => edge.relation === "pivot" || edge.relation === "exposes"),
    [graph.edges],
  );

  const selectedExposures = graph.exposures.filter((row) => row.assetId === selectedAssetId);

  return (
    <section className="grid gap-4 xl:grid-cols-[1.1fr_1fr]">
      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Asset Graph Visualization Engine</h2>
        <svg viewBox="0 0 760 280" className="mt-4 w-full rounded-lg border border-borderSubtle bg-slate-950/70 p-2">
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
          {graph.edges
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
    </section>
  );
}
