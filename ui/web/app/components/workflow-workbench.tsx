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

import React from "react";
import { useEffect, useMemo, useState } from "react";

import {
  defaultWorkflowGraph,
  executionOverlayByNode,
  reorderNodes,
  simulateConcurrentExecutionStates,
  type ExecutionState,
  type WorkflowNode,
} from "../lib/workflow-graph";

const palette: WorkflowNode[] = [
  { id: "p-init", label: "Phishing Access", technique: "T1566", nodeType: "initial_access" },
  { id: "p-priv", label: "Privilege Lift", technique: "T1068", nodeType: "privilege_escalation" },
  { id: "p-lat", label: "Remote Service", technique: "T1021.001", nodeType: "lateral_movement" },
  { id: "p-c2", label: "Beacon Channel", technique: "T1071", nodeType: "c2" },
  { id: "p-exf", label: "Exfil Over C2", technique: "T1041", nodeType: "exfiltration" },
];

const exposureRows = [
  { asset: "vpn.edge.example", title: "Public Admin Interface", value: 0.86 },
  { asset: "api-core-02", title: "Weak Auth", value: 0.63 },
  { asset: "db-finance-01", title: "Legacy TLS", value: 0.74 },
];

const timelineRows = [
  { t: "08:15", label: "Campaign queued", tone: "text-info" },
  { t: "08:23", label: "Initial access validated", tone: "text-telemetryGlow" },
  { t: "08:31", label: "Privilege escalation observed", tone: "text-warning" },
  { t: "08:38", label: "SOC detected suspicious auth chain", tone: "text-critical" },
];

const heatmapRows = [
  { tactic: "TA0001", vals: [0.72, 0.52, 0.41, 0.83] },
  { tactic: "TA0004", vals: [0.68, 0.49, 0.39, 0.75] },
  { tactic: "TA0008", vals: [0.58, 0.35, 0.64, 0.55] },
  { tactic: "TA0011", vals: [0.61, 0.46, 0.73, 0.62] },
];

function severityClass(value: number): string {
  if (value >= 0.75) return "bg-critical";
  if (value >= 0.55) return "bg-warning";
  if (value >= 0.35) return "bg-info";
  return "bg-success";
}

function nodeTypeClass(nodeType: WorkflowNode["nodeType"]): string {
  switch (nodeType) {
    case "initial_access":
      return "text-info";
    case "privilege_escalation":
      return "text-warning";
    case "lateral_movement":
      return "text-telemetryGlow";
    case "exfiltration":
      return "text-critical";
    case "c2":
      return "text-success";
    default:
      return "text-slate-300";
  }
}

function overlayClass(state: ExecutionState): string {
  if (state === "running") return "ring-2 ring-info";
  if (state === "succeeded") return "ring-2 ring-success";
  if (state === "failed") return "ring-2 ring-critical";
  return "ring-1 ring-borderSubtle";
}

export function WorkflowWorkbench() {
  const graph = useMemo(() => defaultWorkflowGraph(), []);
  const [nodes, setNodes] = useState<WorkflowNode[]>(graph.nodes);
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [heatCell, setHeatCell] = useState<{ tactic: string; idx: number } | null>(null);
  const [tick, setTick] = useState(0);
  const [timelineIndex, setTimelineIndex] = useState<number>(timelineRows.length - 1);

  const stateByTechnique = useMemo(() => simulateConcurrentExecutionStates(nodes, tick), [nodes, tick]);
  const overlay = useMemo(() => executionOverlayByNode(nodes, stateByTechnique), [nodes, stateByTechnique]);

  useEffect(() => {
    const timer = setInterval(() => setTick((prev) => prev + 1), 2400);
    return () => clearInterval(timer);
  }, []);

  const telemetryFeed = nodes.slice(0, 4).map((node) => ({
    id: node.id,
    line: `${node.technique} ${overlay[node.id].toUpperCase()} (${node.nodeType})`,
  }));

  return (
    <section className="grid gap-4 xl:grid-cols-[1.1fr_1fr]">
      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Node-Link Execution Canvas</h2>
        <svg viewBox="0 0 720 250" className="mt-4 w-full rounded-lg border border-borderSubtle bg-slate-950/70 p-2">
          {nodes.slice(0, 4).map((node, idx) => {
            const x = 120 + idx * 170;
            const y = idx % 2 === 0 ? 90 : 160;
            const next = nodes[idx + 1];
            if (!next) return null;
            const x2 = 120 + (idx + 1) * 170;
            const y2 = (idx + 1) % 2 === 0 ? 90 : 160;
            return (
              <line key={`edge-${node.id}`} x1={x} y1={y} x2={x2} y2={y2} stroke="#3b82f6" strokeWidth="2" />
            );
          })}

          {nodes.slice(0, 4).map((node, idx) => {
            const x = 120 + idx * 170;
            const y = idx % 2 === 0 ? 90 : 160;
            return (
              <g key={node.id} data-testid={`path-node-${node.id}`}>
                <circle cx={x} cy={y} r={24} fill="#1a2238" stroke="#94a3b8" />
                <text x={x} y={y + 4} fill="#e6e9f5" textAnchor="middle" fontSize="9">
                  {node.technique}
                </text>
              </g>
            );
          })}

          <line x1="120" y1="60" x2="460" y2="40" strokeDasharray="6 4" stroke="#22c55e" strokeWidth="2" />
          <text x="290" y="30" fill="#22c55e" textAnchor="middle" fontSize="10">
            identity-pivot overlay
          </text>
        </svg>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Drag-and-Drop Playbook Builder</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <div className="rounded-lg border border-borderSubtle bg-slate-950/70 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-400">Palette</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {palette.map((node) => (
                <button
                  key={node.id}
                  type="button"
                  className="spectra-button-secondary px-2 py-1 text-xs font-semibold"
                  onClick={() =>
                    setNodes((prev) => [...prev, { ...node, id: `s-${Date.now()}-${node.id}` }])
                  }
                >
                  + {node.label}
                </button>
              ))}
            </div>
          </div>
          <div className="rounded-lg border border-borderSubtle bg-slate-950/70 p-3" data-testid="playbook-list">
            <p className="text-xs uppercase tracking-wide text-slate-400">Execution Node Types</p>
            <ul className="mt-2 space-y-2">
              {nodes.map((node, idx) => (
                <li
                  key={node.id}
                  draggable
                  onDragStart={() => setDraggedId(node.id)}
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={() => {
                    if (!draggedId) return;
                    setNodes((prev) => reorderNodes(prev, draggedId, node.id));
                    setDraggedId(null);
                  }}
                  className={`cursor-move rounded border border-borderSubtle bg-slate-900/80 px-2 py-2 text-sm ${overlayClass(overlay[node.id])}`}
                  data-testid={`playbook-step-${idx + 1}`}
                >
                  <span className="spectra-mono text-telemetryGlow">{idx + 1}.</span> {node.label}{" "}
                  <span className={`spectra-mono ${nodeTypeClass(node.nodeType)}`}>{node.nodeType}</span>
                </li>
              ))}
            </ul>
            <p className="mt-2 text-xs text-slate-400">Branching: always / on_success / on_failure</p>
          </div>
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-info">Real-time Telemetry Streaming Panel</h2>
        <div className="mt-3 rounded-lg border border-borderSubtle bg-slate-950/70 p-3">
          {telemetryFeed.map((item) => (
            <p key={item.id} className="spectra-mono text-sm text-slate-200" data-testid="telemetry-line">
              {item.line}
            </p>
          ))}
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-warning">Interactive ATT&amp;CK Heatmap UI</h2>
        <div className="mt-3 overflow-x-auto rounded-lg border border-borderSubtle">
          <table className="w-full min-w-[440px] text-xs">
            <thead className="bg-slate-900/80 text-slate-300">
              <tr>
                <th className="px-2 py-2 text-left">Tactic</th>
                <th className="px-2 py-2 text-left">A</th>
                <th className="px-2 py-2 text-left">B</th>
                <th className="px-2 py-2 text-left">C</th>
                <th className="px-2 py-2 text-left">D</th>
              </tr>
            </thead>
            <tbody>
              {heatmapRows.map((row) => (
                <tr key={row.tactic} className="border-t border-borderSubtle">
                  <td className="px-2 py-2 spectra-mono">{row.tactic}</td>
                  {row.vals.map((value, idx) => (
                    <td key={`${row.tactic}-${idx}`} className="px-2 py-2">
                      <button
                        type="button"
                        className={`h-6 w-12 rounded ${severityClass(value)}`}
                        data-testid={`heat-cell-${row.tactic}-${idx}`}
                        onClick={() => setHeatCell({ tactic: row.tactic, idx })}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-xs text-slate-300">
          {heatCell ? `Selected ${heatCell.tactic} cell ${heatCell.idx + 1}` : "Select a heatmap cell."}
        </p>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-critical">Exposure Visualization Dashboard</h2>
        <div className="mt-3 grid gap-2">
          {exposureRows.map((row) => (
            <div key={row.asset} className="rounded-lg border border-borderSubtle bg-slate-950/70 p-3">
              <p className="text-xs uppercase tracking-wide text-slate-400">{row.asset}</p>
              <p className="mt-1 text-sm text-slate-200">{row.title}</p>
              <div className="mt-2 h-2 w-full rounded bg-slate-800">
                <div className={`h-2 rounded ${severityClass(row.value)}`} style={{ width: `${Math.round(row.value * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-success">Campaign Timeline Replay View</h2>
        <input
          type="range"
          min={0}
          max={timelineRows.length - 1}
          value={timelineIndex}
          onChange={(event) => setTimelineIndex(Number(event.target.value))}
          className="mt-3 w-full"
          data-testid="timeline-slider"
        />
        <ol className="mt-3 space-y-2">
          {timelineRows.slice(0, timelineIndex + 1).map((row) => (
            <li key={row.t} className="rounded border border-borderSubtle bg-slate-950/70 px-3 py-2 text-sm">
              <span className="spectra-mono text-slate-400">{row.t}</span> <span className={row.tone}>{row.label}</span>
            </li>
          ))}
        </ol>
      </article>
    </section>
  );
}

