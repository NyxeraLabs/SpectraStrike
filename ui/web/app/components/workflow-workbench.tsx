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

"use client";

import "reactflow/dist/style.css";

import React from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import ReactFlow, { Background, Controls, MiniMap, type Edge, type Node } from "reactflow";

import { buildNexusDemoUrl, SPECTRA_ONBOARDED_KEY } from "../lib/demo-mode";
import { useWorkflowStore, type FlowNode, type TelemetryEvent } from "../lib/workflow-store";
import type { RuntimeExecutionState, WorkflowEdge } from "../lib/workflow-graph";

function nodeTypeClass(nodeType: string): string {
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

function overlayClass(state: RuntimeExecutionState): string {
  if (state === "running") return "ring-2 ring-info";
  if (state === "completed") return "ring-2 ring-success";
  if (state === "retrying") return "ring-2 ring-warning";
  if (state === "blocked") return "ring-2 ring-warning";
  if (state === "failed") return "ring-2 ring-critical";
  return "ring-1 ring-borderSubtle";
}

function nodeLabel(node: Node<{ label: string; technique: string; nodeType: string; wrapperKey?: string }>): string {
  return `${node.data.label} (${node.data.technique})`;
}

export function WorkflowWorkbench() {
  const nodes = useWorkflowStore((state) => state.nodes);
  const edges = useWorkflowStore((state) => state.edges);
  const queue = useWorkflowStore((state) => state.queue);
  const wrappers = useWorkflowStore((state) => state.wrappers);
  const telemetry = useWorkflowStore((state) => state.telemetry);
  const executionStatus = useWorkflowStore((state) => state.executionStatus);
  const statusMessage = useWorkflowStore((state) => state.statusMessage);
  const edgeBranch = useWorkflowStore((state) => state.edgeBranch);
  const spectraDemoActive = useWorkflowStore((state) => state.spectraDemoActive);
  const spectraDemoStep = useWorkflowStore((state) => state.spectraDemoStep);

  const setFromBackend = useWorkflowStore((state) => state.setFromBackend);
  const setWrappers = useWorkflowStore((state) => state.setWrappers);
  const setTelemetry = useWorkflowStore((state) => state.setTelemetry);
  const setExecutionStatus = useWorkflowStore((state) => state.setExecutionStatus);
  const setStatusMessage = useWorkflowStore((state) => state.setStatusMessage);
  const setEdgeBranch = useWorkflowStore((state) => state.setEdgeBranch);
  const seedDemoPlaybook = useWorkflowStore((state) => state.seedDemoPlaybook);
  const nextDemoStep = useWorkflowStore((state) => state.nextDemoStep);
  const dismissDemo = useWorkflowStore((state) => state.dismissDemo);
  const enableDemo = useWorkflowStore((state) => state.enableDemo);
  const onNodesChange = useWorkflowStore((state) => state.onNodesChange);
  const onEdgesChange = useWorkflowStore((state) => state.onEdgesChange);
  const onConnect = useWorkflowStore((state) => state.onConnect);
  const addWrapperNode = useWorkflowStore((state) => state.addWrapperNode);
  const addPrivilegeLiftNode = useWorkflowStore((state) => state.addPrivilegeLiftNode);
  const duplicateNode = useWorkflowStore((state) => state.duplicateNode);
  const removeNode = useWorkflowStore((state) => state.removeNode);
  const queueNode = useWorkflowStore((state) => state.queueNode);
  const removeQueuedNode = useWorkflowStore((state) => state.removeQueuedNode);
  const moveQueueUp = useWorkflowStore((state) => state.moveQueueUp);
  const moveQueueDown = useWorkflowStore((state) => state.moveQueueDown);
  const addManualEdge = useWorkflowStore((state) => state.addManualEdge);
  const removeEdge = useWorkflowStore((state) => state.removeEdge);
  const getPersistencePayload = useWorkflowStore((state) => state.getPersistencePayload);

  const [edgeSource, setEdgeSource] = useState<string>("");
  const [edgeTarget, setEdgeTarget] = useState<string>("");
  const [canvasFullscreen, setCanvasFullscreen] = useState(false);

  const nodesRef = useRef<FlowNode[]>(nodes);
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const onboarded = window.localStorage.getItem(SPECTRA_ONBOARDED_KEY) === "true";
    if (!onboarded) {
      enableDemo();
      setStatusMessage("Guided first-run demo is active.");
    }
  }, [enableDemo, setStatusMessage]);

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch("/ui/api/execution/wrappers").then((res) => res.json()),
      fetch("/ui/api/execution/playbook").then((res) => res.json()),
      fetch("/ui/api/execution/queue?limit=50").then((res) => res.json()),
      fetch("/ui/api/telemetry/events?limit=25").then((res) => res.json()),
    ])
      .then(([wrapperBody, playbookBody, queueBody, telemetryBody]) => {
        if (!active) return;
        setWrappers(Array.isArray(wrapperBody.items) ? wrapperBody.items : []);

        if (Array.isArray(playbookBody.nodes) && Array.isArray(playbookBody.edges) && Array.isArray(playbookBody.queue)) {
          setFromBackend({
            nodes: playbookBody.nodes,
            edges: playbookBody.edges,
            queue: playbookBody.queue,
          });
          setStatusMessage("Playbook loaded from backend.");
        }

        if (Array.isArray(queueBody.items)) {
          setExecutionStatus(() => {
            const next: Record<string, RuntimeExecutionState> = {};
            for (const item of queueBody.items) {
              const status = String(item.status) as RuntimeExecutionState;
              if (status !== "queued" && status !== "running" && status !== "blocked" && status !== "retrying" && status !== "failed" && status !== "completed") {
                continue;
              }
              const tool = String(item.tool ?? "");
              for (const node of playbookBody.nodes ?? []) {
                if (String(node.wrapperKey ?? "") === tool) {
                  next[String(node.id)] = status;
                }
              }
            }
            return next;
          });
        }

        if (Array.isArray(telemetryBody.items)) {
          setTelemetry(telemetryBody.items as TelemetryEvent[]);
        }
      })
      .catch(() => setStatusMessage("Unable to load backend execution surfaces."));

    return () => {
      active = false;
    };
  }, [setExecutionStatus, setFromBackend, setStatusMessage, setTelemetry, setWrappers]);

  useEffect(() => {
    if (!spectraDemoActive) return;
    if (spectraDemoStep !== "auto_build_playbook") return;
    seedDemoPlaybook();
  }, [seedDemoPlaybook, spectraDemoActive, spectraDemoStep]);

  useEffect(() => {
    const stream = new EventSource("/ui/api/execution/stream");
    stream.addEventListener("diagnostic", (event) => {
      const payload = JSON.parse((event as MessageEvent<string>).data);
      setStatusMessage(`Execution stream mode=${payload.mode} detail=${payload.detail}`);
    });
    stream.addEventListener("status_snapshot", (event) => {
      const payload = JSON.parse((event as MessageEvent<string>).data);
      if (!Array.isArray(payload.items)) return;
      setExecutionStatus((prev) => {
        const next = { ...prev };
        for (const item of payload.items) {
          const status = String(item.status) as RuntimeExecutionState;
          if (status !== "queued" && status !== "running" && status !== "blocked" && status !== "retrying" && status !== "failed" && status !== "completed") {
            continue;
          }
          const tool = String(item.tool ?? "");
          for (const node of nodesRef.current) {
            if (String(node.data.wrapperKey ?? "") === tool) {
              next[node.id] = status;
            }
          }
        }
        return next;
      });
    });
    return () => stream.close();
  }, [setExecutionStatus, setStatusMessage]);

  useEffect(() => {
    const id = setTimeout(() => {
      const payload = getPersistencePayload();
      fetch("/ui/api/execution/playbook", {
        method: "PUT",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      }).catch(() => undefined);
    }, 350);
    return () => clearTimeout(id);
  }, [nodes, edges, queue, getPersistencePayload]);

  const overlay = useMemo(() => {
    const out: Record<string, RuntimeExecutionState> = {};
    for (const node of nodes) {
      out[node.id] = executionStatus[node.id] ?? "queued";
    }
    return out;
  }, [executionStatus, nodes]);

  const renderedNodes = useMemo(() => {
    return nodes.map((node) => ({
      ...node,
      className: overlayClass(overlay[node.id]),
      data: {
        ...node.data,
        label: `${node.data.label} [${overlay[node.id]}]`,
      },
    }));
  }, [nodes, overlay]);

  const renderedEdges = useMemo(() => {
    return edges.map((edge) => {
      const branch = edge.data?.branchCondition ?? "always";
      return {
        ...edge,
        label: branch,
        animated: branch === "on_success",
      };
    });
  }, [edges]);

  async function executeQueue() {
    for (const nodeId of queue) {
      const node = nodes.find((item) => item.id === nodeId);
      if (!node) continue;
      setExecutionStatus((prev) => ({ ...prev, [node.id]: "running" }));
      try {
        const response = await fetch("/ui/api/actions/tasks", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            tool: node.data.wrapperKey ?? "nmap",
            target: "127.0.0.1",
            parameters: { technique: node.data.technique, demoMode: spectraDemoActive },
          }),
        });
        if (!response.ok) {
          setExecutionStatus((prev) => ({ ...prev, [node.id]: "failed" }));
          continue;
        }
        setExecutionStatus((prev) => ({ ...prev, [node.id]: "completed" }));
      } catch {
        setExecutionStatus((prev) => ({ ...prev, [node.id]: "retrying" }));
      }
    }

    if (spectraDemoActive && spectraDemoStep === "execute_demo") {
      nextDemoStep();
    }
  }

  const federationDiagnostics = telemetry
    .filter((item) => item.envelope_id || item.failure_reason || item.signature_state)
    .slice(0, 5);

  return (
    <section className="grid gap-4 xl:grid-cols-[1.1fr_1fr]">
      {spectraDemoActive ? (
        <article className="spectra-panel p-5 xl:col-span-2">
          <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Assisted First-Run Demo</h2>
          <p className="mt-2 text-sm text-slate-300">
            Demo step: <span className="spectra-mono">{spectraDemoStep}</span>
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" className="spectra-button-primary px-3 py-2 text-sm font-semibold" onClick={nextDemoStep}>
              Next Demo Step
            </button>
            {spectraDemoStep === "open_nexus" || spectraDemoStep === "complete" ? (
              <a href={buildNexusDemoUrl()} className="spectra-button-secondary px-3 py-2 text-sm font-semibold">
                Open Nexus Demo
              </a>
            ) : null}
            <button
              type="button"
              className="spectra-button-secondary px-3 py-2 text-sm font-semibold"
              onClick={() => {
                dismissDemo();
                if (typeof window !== "undefined") {
                  window.localStorage.setItem(SPECTRA_ONBOARDED_KEY, "true");
                }
              }}
            >
              Finish / Dismiss Demo
            </button>
          </div>
        </article>
      ) : null}

      <article className="spectra-panel p-5">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Node-Link Execution Canvas</h2>
          <button
            type="button"
            className="spectra-button-secondary px-3 py-1.5 text-xs"
            onClick={() => setCanvasFullscreen((current) => !current)}
          >
            {canvasFullscreen ? "Exit Full Screen" : "Full Screen"}
          </button>
        </div>
        <div className={`relative mt-4 w-full overflow-hidden rounded-lg border border-borderSubtle bg-slate-950/70 p-2 ${canvasFullscreen ? "fixed inset-4 z-50 h-[calc(100vh-2rem)]" : "h-[500px]"}`}>
          <ReactFlow
            nodes={renderedNodes as Node[]}
            edges={renderedEdges as Edge[]}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
          >
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
          {canvasFullscreen ? (
            <button
              type="button"
              className="spectra-button-secondary absolute right-4 top-4 z-10 px-3 py-1.5 text-xs"
              onClick={() => setCanvasFullscreen(false)}
            >
              Close
            </button>
          ) : null}
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Backend-Persisted Playbook Builder</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <div className="rounded-lg border border-borderSubtle bg-slate-950/70 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-400">Wrapper Palette (Full Surface)</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {wrappers.map((wrapper) => (
                <button
                  key={wrapper.key}
                  type="button"
                  className="spectra-button-secondary px-2 py-1 text-xs font-semibold"
                  onClick={() => addWrapperNode(wrapper)}
                >
                  + {wrapper.label}
                </button>
              ))}
              <button
                type="button"
                className="spectra-button-secondary px-2 py-1 text-xs font-semibold"
                onClick={addPrivilegeLiftNode}
              >
                + Privilege Lift
              </button>
            </div>
          </div>
          <div className="rounded-lg border border-borderSubtle bg-slate-950/70 p-3" data-testid="playbook-list">
            <p className="text-xs uppercase tracking-wide text-slate-400">Execution Node Types</p>
            <ul className="mt-2 space-y-2">
              {nodes.map((node, idx) => (
                <li
                  key={node.id}
                  className={`rounded border border-borderSubtle bg-slate-900/80 px-2 py-2 text-sm ${overlayClass(overlay[node.id])}`}
                  data-testid={`playbook-step-${idx + 1}`}
                >
                  <span className="spectra-mono text-telemetryGlow">{idx + 1}.</span> {node.data.label}{" "}
                  <span className={`spectra-mono ${nodeTypeClass(node.data.nodeType)}`}>{node.data.nodeType}</span>
                  <span className="ml-2 text-xs text-slate-400">{node.data.wrapperKey ?? "unbound-wrapper"}</span>
                  <div className="mt-2 flex gap-2">
                    <button
                      type="button"
                      className="spectra-button-secondary px-2 py-1 text-xs"
                      onClick={() => duplicateNode(node.id)}
                    >
                      duplicate
                    </button>
                    <button
                      type="button"
                      className="spectra-button-secondary px-2 py-1 text-xs"
                      onClick={() => removeNode(node.id)}
                    >
                      remove
                    </button>
                    <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => queueNode(node.id)}>
                      queue
                    </button>
                  </div>
                </li>
              ))}
            </ul>
            <div className="mt-3 rounded border border-borderSubtle p-2 text-xs">
              <p className="text-slate-300">Branching / Edge Builder</p>
              <div className="mt-2 grid gap-2 md:grid-cols-4">
                <select className="bg-slate-950 px-2 py-1" value={edgeSource} onChange={(event) => setEdgeSource(event.target.value)}>
                  <option value="">source</option>
                  {nodes.map((node) => (
                    <option key={node.id} value={node.id}>{nodeLabel(node)}</option>
                  ))}
                </select>
                <select className="bg-slate-950 px-2 py-1" value={edgeTarget} onChange={(event) => setEdgeTarget(event.target.value)}>
                  <option value="">target</option>
                  {nodes.map((node) => (
                    <option key={node.id} value={node.id}>{nodeLabel(node)}</option>
                  ))}
                </select>
                <select
                  className="bg-slate-950 px-2 py-1"
                  value={edgeBranch}
                  onChange={(event) => setEdgeBranch(event.target.value as WorkflowEdge["branchCondition"])}
                >
                  <option value="always">always</option>
                  <option value="on_success">on_success</option>
                  <option value="on_failure">on_failure</option>
                </select>
                <button
                  type="button"
                  className="spectra-button-primary px-2 py-1"
                  onClick={() => addManualEdge(edgeSource, edgeTarget)}
                >
                  add edge
                </button>
              </div>
              <ul className="mt-2 space-y-1">
                {edges.map((edge) => (
                  <li key={edge.id} className="flex items-center justify-between rounded border border-borderSubtle px-2 py-1">
                    <span>{edge.source} {"->"} {edge.target} ({edge.data?.branchCondition ?? "always"})</span>
                    <button type="button" className="spectra-button-secondary px-2 py-0.5 text-xs" onClick={() => removeEdge(edge.id)}>
                      remove
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-info">Execution Queue + Live Stream</h2>
        <p className="mt-2 text-xs text-slate-400">{statusMessage}</p>
        <div className="mt-3 rounded-lg border border-borderSubtle bg-slate-950/70 p-3">
          <ol className="space-y-2">
            {queue.map((nodeId, idx) => (
              <li key={nodeId} className="flex items-center justify-between rounded border border-borderSubtle px-2 py-2 text-sm">
                <span>{idx + 1}. {nodes.find((node) => node.id === nodeId)?.data.label ?? nodeId}</span>
                <div className="flex gap-1">
                  <button type="button" className="spectra-button-secondary px-2 py-0.5 text-xs" onClick={() => moveQueueUp(nodeId)}>
                    up
                  </button>
                  <button type="button" className="spectra-button-secondary px-2 py-0.5 text-xs" onClick={() => moveQueueDown(nodeId)}>
                    down
                  </button>
                  <button type="button" className="spectra-button-secondary px-2 py-0.5 text-xs" onClick={() => removeQueuedNode(nodeId)}>
                    remove
                  </button>
                </div>
              </li>
            ))}
          </ol>
          <button type="button" className="spectra-button-primary mt-3 px-3 py-2 text-sm font-semibold" onClick={executeQueue}>
            Execute Queue
          </button>
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-warning">Telemetry + Federation Diagnostics</h2>
        <div className="mt-3 grid gap-3">
          <div className="rounded border border-borderSubtle bg-slate-950/70 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-400">Execution Logs / Raw Output</p>
            {telemetry.slice(0, 6).map((item) => (
              <pre key={item.event_id} className="spectra-mono mt-2 overflow-x-auto text-xs text-slate-200">
                {JSON.stringify(item, null, 2)}
              </pre>
            ))}
          </div>
          <div className="rounded border border-borderSubtle bg-slate-950/70 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-400">Federation Diagnostics</p>
            {federationDiagnostics.length === 0 ? (
              <p className="mt-2 text-xs text-slate-300">No envelope diagnostics emitted yet.</p>
            ) : (
              <ul className="mt-2 space-y-2 text-xs">
                {federationDiagnostics.map((item) => (
                  <li key={`${item.event_id}-diag`} className="rounded border border-borderSubtle p-2">
                    <p>Envelope ID: {item.envelope_id ?? "n/a"}</p>
                    <p>Signature state: {item.signature_state ?? "n/a"}</p>
                    <p>Failure reason: {item.failure_reason ?? "none"}</p>
                    <p>Retry attempts: {item.retry_attempts ?? 0}</p>
                    <p>VectorVue response: {item.vectorvue_response ?? "n/a"}</p>
                    <p>Attestation proof: {item.attestation_proof ?? "n/a"}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </article>
    </section>
  );
}
