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

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  type ReactFlowInstance,
} from "reactflow";

import { SPECTRA_ONBOARDED_KEY } from "../lib/demo-mode";
import {
  safeLocalStorageGet,
  safeLocalStorageSet,
} from "../lib/browser-storage";
import { useFullscreenController } from "../lib/fullscreen-controller";
import type { WrapperDescriptor } from "../lib/wrapper-registry";
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

type SpectraBootstrapStatus = {
  users: number;
  tenants: number;
  keys: number;
  wrapper_configured: number;
  federation_configured: number;
  is_db_zero: boolean;
  platform_onboarded: boolean;
};

const PICKER_SECTIONS: { key: string; title: string }[] = [
  { key: "recon", title: "Recon" },
  { key: "initial_access", title: "Initial Access" },
  { key: "privilege_escalation", title: "PrivEsc" },
  { key: "lateral_movement", title: "Lateral Movement" },
  { key: "c2", title: "C2" },
  { key: "exfiltration", title: "Exfiltration" },
  { key: "infra", title: "Infrastructure" },
  { key: "custom", title: "Custom Wrappers" },
];

function pickerBucketForWrapper(wrapper: WrapperDescriptor): string {
  if (wrapper.nodeType === "initial_access" && wrapper.category === "recon") return "recon";
  if (wrapper.nodeType === "initial_access") return "initial_access";
  if (wrapper.nodeType === "privilege_escalation") return "privilege_escalation";
  if (wrapper.nodeType === "lateral_movement") return "lateral_movement";
  if (wrapper.nodeType === "c2") return "c2";
  if (wrapper.nodeType === "exfiltration") return "exfiltration";
  if (wrapper.category === "cloud" || wrapper.category === "network") return "infra";
  return "custom";
}

function sameStringList(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  for (let idx = 0; idx < a.length; idx += 1) {
    if (a[idx] !== b[idx]) return false;
  }
  return true;
}

function parseSsePayload(raw: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(raw);
    return typeof parsed === "object" && parsed !== null ? (parsed as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
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
  const setFromBackend = useWorkflowStore((state) => state.setFromBackend);
  const setWrappers = useWorkflowStore((state) => state.setWrappers);
  const setTelemetry = useWorkflowStore((state) => state.setTelemetry);
  const setExecutionStatus = useWorkflowStore((state) => state.setExecutionStatus);
  const setStatusMessage = useWorkflowStore((state) => state.setStatusMessage);
  const setEdgeBranch = useWorkflowStore((state) => state.setEdgeBranch);
  const registerDemoAction = useWorkflowStore((state) => state.registerDemoAction);
  const onNodesChange = useWorkflowStore((state) => state.onNodesChange);
  const onEdgesChange = useWorkflowStore((state) => state.onEdgesChange);
  const onConnect = useWorkflowStore((state) => state.onConnect);
  const addWrapperNode = useWorkflowStore((state) => state.addWrapperNode);
  const addWrapperNodeAt = useWorkflowStore((state) => state.addWrapperNodeAt);
  const updateNodeConfig = useWorkflowStore((state) => state.updateNodeConfig);
  const addPrivilegeLiftNode = useWorkflowStore((state) => state.addPrivilegeLiftNode);
  const duplicateNode = useWorkflowStore((state) => state.duplicateNode);
  const removeNode = useWorkflowStore((state) => state.removeNode);
  const removeNodes = useWorkflowStore((state) => state.removeNodes);
  const queueNode = useWorkflowStore((state) => state.queueNode);
  const removeQueuedNode = useWorkflowStore((state) => state.removeQueuedNode);
  const moveQueueUp = useWorkflowStore((state) => state.moveQueueUp);
  const moveQueueDown = useWorkflowStore((state) => state.moveQueueDown);
  const addManualEdge = useWorkflowStore((state) => state.addManualEdge);
  const removeEdge = useWorkflowStore((state) => state.removeEdge);
  const getPersistencePayload = useWorkflowStore((state) => state.getPersistencePayload);

  const [edgeSource, setEdgeSource] = useState<string>("");
  const [edgeTarget, setEdgeTarget] = useState<string>("");
  const [pickerOpen, setPickerOpen] = useState(true);
  const [pickerQuery, setPickerQuery] = useState("");
  const [pickerFilter, setPickerFilter] = useState("all");
  const [pickerSectionOpen, setPickerSectionOpen] = useState<Record<string, boolean>>(
    () => Object.fromEntries(PICKER_SECTIONS.map((section) => [section.key, true])),
  );
  const [activeTab, setActiveTab] = useState<"logs" | "telemetry" | "signature">("logs");
  const [selectedNodeIds, setSelectedNodeIds] = useState<string[]>([]);
  const [configNodeId, setConfigNodeId] = useState<string | null>(null);
  const [configTarget, setConfigTarget] = useState("127.0.0.1");
  const [configProfile, setConfigProfile] = useState("default");
  const [bootstrapStatus, setBootstrapStatus] = useState<SpectraBootstrapStatus | null>(null);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [wizardStep, setWizardStep] = useState(1);
  const [wizardWorkspace, setWizardWorkspace] = useState("spectra-workspace");
  const [wizardWrappers, setWizardWrappers] = useState<string[]>(["nmap", "metasploit", "sliver"]);
  const [wizardFederationEndpoint, setWizardFederationEndpoint] = useState("http://localhost:8000");

  const canvasHostRef = useRef<HTMLDivElement | null>(null);
  const nodesRef = useRef<FlowNode[]>(nodes);
  const reactFlowApiRef = useRef<ReactFlowInstance | null>(null);
  const fullscreen = useFullscreenController();
  const canvasFullscreen = fullscreen.isFullscreen;

  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  useEffect(() => {
    const onboarded = safeLocalStorageGet(SPECTRA_ONBOARDED_KEY) === "true";
    if (!onboarded) {
      setStatusMessage("First-run configuration is required.");
      setWizardOpen(true);
    }
  }, [setStatusMessage]);

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch("/ui/api/execution/wrappers").then((res) => res.json()),
      fetch("/ui/api/execution/playbook").then((res) => res.json()),
      fetch("/ui/api/execution/queue?limit=50").then((res) => res.json()),
      fetch("/ui/api/telemetry/events?limit=25").then((res) => res.json()),
      fetch("/ui/api/bootstrap/status").then((res) => res.json()).catch(() => null),
    ])
      .then(([wrapperBody, playbookBody, queueBody, telemetryBody, bootstrapBody]) => {
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

        const queueItems = Array.isArray(queueBody.items) ? queueBody.items : [];
        const playbookNodes = Array.isArray(playbookBody?.nodes) ? playbookBody.nodes : [];
        if (queueItems.length > 0) {
          setExecutionStatus(() => {
            const next: Record<string, RuntimeExecutionState> = {};
            for (const item of queueItems) {
              if (!isRecord(item)) continue;
              const status = String(item.status ?? "") as RuntimeExecutionState;
              if (status !== "queued" && status !== "running" && status !== "blocked" && status !== "retrying" && status !== "failed" && status !== "completed") {
                continue;
              }
              const tool = String(item.tool ?? "");
              for (const node of playbookNodes) {
                if (!isRecord(node)) continue;
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

        const status = bootstrapBody?.status as SpectraBootstrapStatus | undefined;
        if (status) {
          setBootstrapStatus(status);
          if (status.is_db_zero || status.platform_onboarded === false) {
            setWizardOpen(true);
          }
        }
      })
      .catch(() => setStatusMessage("Unable to load backend execution surfaces."));

    return () => {
      active = false;
    };
  }, [setExecutionStatus, setFromBackend, setStatusMessage, setTelemetry, setWrappers]);

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.EventSource === "undefined") {
      setStatusMessage("Execution stream unavailable in this browser.");
      return;
    }
    let stream: EventSource;
    try {
      stream = new EventSource("/ui/api/execution/stream");
    } catch {
      setStatusMessage("Unable to initialize execution stream.");
      return;
    }
    stream.addEventListener("diagnostic", (event) => {
      const payload = parseSsePayload((event as MessageEvent<string>).data);
      if (!payload) return;
      setStatusMessage(
        `Execution stream mode=${String(payload.mode ?? "unknown")} detail=${String(payload.detail ?? "none")}`,
      );
    });
    stream.addEventListener("status_snapshot", (event) => {
      const payload = parseSsePayload((event as MessageEvent<string>).data);
      const snapshotItems = payload?.items;
      if (!Array.isArray(snapshotItems)) return;
      setExecutionStatus((prev) => {
        const next = { ...prev };
        for (const item of snapshotItems) {
          if (typeof item !== "object" || item === null) continue;
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

  useEffect(() => {
    const handleDelete = (event: KeyboardEvent) => {
      if ((event.key !== "Delete" && event.key !== "Backspace") || selectedNodeIds.length === 0) {
        return;
      }
      removeNodes(selectedNodeIds);
      setSelectedNodeIds([]);
    };
    window.addEventListener("keydown", handleDelete);
    return () => window.removeEventListener("keydown", handleDelete);
  }, [removeNodes, selectedNodeIds]);

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

  const wrappersBySection = useMemo(() => {
    const grouped: Record<string, WrapperDescriptor[]> = {};
    const normalizedQuery = pickerQuery.trim().toLowerCase();
    for (const section of PICKER_SECTIONS) {
      grouped[section.key] = [];
    }
    for (const wrapper of wrappers) {
      const bucket = pickerBucketForWrapper(wrapper);
      if (pickerFilter !== "all" && bucket !== pickerFilter) continue;
      if (normalizedQuery) {
        const searchable = `${wrapper.label} ${wrapper.key} ${wrapper.category} ${wrapper.description}`.toLowerCase();
        if (!searchable.includes(normalizedQuery)) continue;
      }
      grouped[bucket] = grouped[bucket] ?? [];
      grouped[bucket].push(wrapper);
    }
    return grouped;
  }, [pickerFilter, pickerQuery, wrappers]);

  const configNode = configNodeId ? nodes.find((node) => node.id === configNodeId) : null;

  async function executeQueue() {
    registerDemoAction("execution_started");
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
            target: node.data.config?.target ?? "127.0.0.1",
            parameters: {
              technique: node.data.technique,
              profile: node.data.config?.profile ?? "default",
            },
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
  }

  async function toggleFullscreen() {
    await fullscreen.toggle();
  }

  const onDragStartWrapper = useCallback((event: React.DragEvent, wrapperKey: string) => {
    event.dataTransfer.setData("application/spectrastrike-wrapper", wrapperKey);
    event.dataTransfer.effectAllowed = "move";
  }, []);

  const onDropWrapper = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const wrapperKey = event.dataTransfer.getData("application/spectrastrike-wrapper");
      const reactFlowApi = reactFlowApiRef.current;
      if (!wrapperKey || !reactFlowApi || !canvasHostRef.current) {
        return;
      }
      const wrapper = wrappers.find((item) => item.key === wrapperKey);
      if (!wrapper) return;
      const hostRect = canvasHostRef.current.getBoundingClientRect();
      const projected = reactFlowApi.project({
        x: event.clientX - hostRect.left,
        y: event.clientY - hostRect.top,
      });
      addWrapperNodeAt(wrapper, projected.x, projected.y);
      registerDemoAction("node_dragged");
    },
    [addWrapperNodeAt, wrappers, registerDemoAction],
  );

  const federationDiagnostics = telemetry
    .filter((item) => item.envelope_id || item.failure_reason || item.signature_state)
    .slice(0, 5);

  async function completeWizard() {
    await fetch("/ui/api/bootstrap/setup", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        workspace_name: wizardWorkspace,
        wrappers: wizardWrappers,
        federation_endpoint: wizardFederationEndpoint,
      }),
    }).catch(() => undefined);
    setWizardOpen(false);
    safeLocalStorageSet(SPECTRA_ONBOARDED_KEY, "true");
  }

  return (
    <section className="grid gap-4 xl:grid-cols-[320px_1fr]" data-testid="workflow-workbench-root">
      {wizardOpen ? (
        <article className="spectra-panel p-5 xl:col-span-2" data-testid="first-run-wizard">
          <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">First Run Bootstrap Wizard</h2>
          <p className="mt-2 text-xs text-slate-300">
            DB-zero status: users={bootstrapStatus?.users ?? 0} tenants={bootstrapStatus?.tenants ?? 0} keys={bootstrapStatus?.keys ?? 0} wrappers={bootstrapStatus?.wrapper_configured ?? 0} federation={bootstrapStatus?.federation_configured ?? 0}
          </p>
          <div className="mt-3 h-2 rounded bg-slate-900">
            <div className="h-2 rounded bg-accentPrimary" style={{ width: `${Math.min(100, Math.max(0, wizardStep * 16.6))}%` }} />
          </div>
          {wizardStep === 1 ? (
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              <label className="text-sm">
                Workspace name
                <input value={wizardWorkspace} onChange={(event) => setWizardWorkspace(event.target.value)} className="mt-1 w-full rounded border border-borderSubtle bg-slate-950 px-2 py-1" />
              </label>
            </div>
          ) : null}
          {wizardStep === 2 ? (
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              {wrappers.slice(0, 12).map((wrapper) => {
                const selected = wizardWrappers.includes(wrapper.key);
                return (
                  <button
                    key={wrapper.key}
                    type="button"
                    onClick={() => {
                      setWizardWrappers((current) =>
                        current.includes(wrapper.key)
                          ? current.filter((value) => value !== wrapper.key)
                          : [...current, wrapper.key],
                      );
                    }}
                    className={`rounded border px-2 py-1 text-left text-xs ${selected ? "border-accentPrimary text-white" : "border-borderSubtle text-slate-300"}`}
                  >
                    {wrapper.label}
                  </button>
                );
              })}
            </div>
          ) : null}
          {wizardStep === 3 ? (
            <label className="mt-3 block text-sm">
              Federation endpoint
              <input value={wizardFederationEndpoint} onChange={(event) => setWizardFederationEndpoint(event.target.value)} className="mt-1 w-full rounded border border-borderSubtle bg-slate-950 px-2 py-1" />
            </label>
          ) : null}
          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" className="spectra-button-secondary px-3 py-2 text-sm" onClick={() => setWizardStep((current) => Math.max(1, current - 1))}>
              Back
            </button>
            {wizardStep < 6 ? (
              <button type="button" className="spectra-button-primary px-3 py-2 text-sm" onClick={() => setWizardStep((current) => Math.min(6, current + 1))}>
                Continue
              </button>
            ) : (
              <button type="button" className="spectra-button-primary px-3 py-2 text-sm" onClick={completeWizard}>
                Confirm Environment Ready
              </button>
            )}
            <button type="button" className="spectra-button-secondary px-3 py-2 text-sm" onClick={() => setWizardOpen(false)}>
              Skip for Now
            </button>
          </div>
        </article>
      ) : null}

      <article className="spectra-panel p-4" data-testid="component-picker-panel">
        <div className="flex items-center justify-between">
          <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Component Picker</h2>
          <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => setPickerOpen((current) => !current)}>
            {pickerOpen ? "Collapse" : "Expand"}
          </button>
        </div>
        {pickerOpen ? (
          <div className="mt-3 max-h-[72vh] overflow-y-auto pr-1">
            <div className="mb-3 grid gap-2">
              <input
                value={pickerQuery}
                onChange={(event) => setPickerQuery(event.target.value)}
                className="w-full rounded border border-borderSubtle bg-slate-950 px-2 py-1 text-xs"
                placeholder="Search wrappers"
              />
              <select
                value={pickerFilter}
                onChange={(event) => setPickerFilter(event.target.value)}
                className="w-full rounded border border-borderSubtle bg-slate-950 px-2 py-1 text-xs"
              >
                <option value="all">All categories</option>
                {PICKER_SECTIONS.map((section) => (
                  <option key={`filter-${section.key}`} value={section.key}>
                    {section.title}
                  </option>
                ))}
              </select>
            </div>
            {PICKER_SECTIONS.map((section) => (
              <div key={section.key} className="mb-3 rounded border border-borderSubtle p-2">
                <button
                  type="button"
                  className="flex w-full items-center justify-between text-xs uppercase tracking-wide text-slate-400"
                  onClick={() =>
                    setPickerSectionOpen((current) => ({
                      ...current,
                      [section.key]: !current[section.key],
                    }))
                  }
                >
                  <span>{section.title}</span>
                  <span>{pickerSectionOpen[section.key] ? "−" : "+"}</span>
                </button>
                {pickerSectionOpen[section.key] ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(wrappersBySection[section.key] ?? []).map((wrapper) => (
                      <button
                        key={wrapper.key}
                        type="button"
                        draggable
                        onDragStart={(event) => onDragStartWrapper(event, wrapper.key)}
                        onClick={() => {
                          addWrapperNode(wrapper);
                          registerDemoAction("node_dragged");
                        }}
                        className="rounded border border-borderSubtle bg-slate-950 px-2 py-1 text-left text-xs hover:border-accentPrimary"
                        title={wrapper.description}
                      >
                        {wrapper.label}
                      </button>
                    ))}
                    {(wrappersBySection[section.key] ?? []).length === 0 ? (
                      <p className="text-xs text-slate-500">No wrappers in this section.</p>
                    ) : null}
                  </div>
                ) : null}
              </div>
            ))}
            <button
              type="button"
              className="spectra-button-secondary w-full px-2 py-1 text-xs"
              onClick={() => {
                addPrivilegeLiftNode();
                registerDemoAction("node_dragged");
              }}
            >
              + Privilege Lift
            </button>
          </div>
        ) : null}
      </article>

      <article className="space-y-4">

        <div className="spectra-panel p-5">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Node-Link Execution Canvas</h2>
            <button type="button" className="spectra-button-secondary px-3 py-1.5 text-xs" onClick={toggleFullscreen}>
              {canvasFullscreen ? "Exit Full Screen" : "Full Screen"}
            </button>
          </div>
          <div
            ref={canvasHostRef}
            onDrop={onDropWrapper}
            onDragOver={(event) => event.preventDefault()}
            className={`relative mt-4 w-full overflow-hidden rounded-lg border border-borderSubtle bg-slate-950/70 ${canvasFullscreen ? "canvas-fullscreen z-[9999] border-none rounded-none" : "h-[520px]"}`}
          >
            <ReactFlow
              nodes={renderedNodes as Node[]}
              edges={renderedEdges as Edge[]}
              onInit={(instance) => {
                reactFlowApiRef.current = instance;
              }}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={(connection) => {
              onConnect(connection);
              registerDemoAction("nodes_connected");
            }}
            onSelectionChange={(params) => {
              const selected = (params.nodes ?? []).map((node) => node.id);
              setSelectedNodeIds((current) => (sameStringList(current, selected) ? current : selected));
            }}
              fitView
              minZoom={0.2}
              maxZoom={2.5}
              multiSelectionKeyCode={["Shift"]}
              panOnScroll
            >
              <MiniMap />
              <Controls />
              <Background />
            </ReactFlow>
            {canvasFullscreen ? (
              <button type="button" className="spectra-button-secondary absolute right-4 top-4 z-10 px-3 py-1.5 text-xs" onClick={toggleFullscreen}>
                Close
              </button>
            ) : null}
            {nodes.length === 0 ? (
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center text-sm text-slate-400">
                Drag components from the picker or click a component to auto place.
              </div>
            ) : null}
          </div>
        </div>

        <div className="spectra-panel p-5" data-testid="playbook-list">
          <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Playbook Builder</h2>
          <ul className="mt-3 space-y-2">
            {nodes.map((node, idx) => (
              <li key={node.id} className={`rounded border border-borderSubtle bg-slate-900/80 px-2 py-2 text-sm ${overlayClass(overlay[node.id])}`} data-testid={`playbook-step-${idx + 1}`}>
                <span className="spectra-mono text-telemetryGlow">{idx + 1}.</span> {node.data.label} <span className={`spectra-mono ${nodeTypeClass(node.data.nodeType)}`}>{node.data.nodeType}</span>
                <span className="ml-2 text-xs text-slate-400">{node.data.wrapperKey ?? "unbound-wrapper"}</span>
                <div className="mt-2 flex flex-wrap gap-2">
                  <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => duplicateNode(node.id)}>duplicate</button>
                  <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => removeNode(node.id)}>remove</button>
                  <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => { queueNode(node.id); registerDemoAction("queued"); }}>queue</button>
                  <button
                    type="button"
                    className="spectra-button-secondary px-2 py-1 text-xs"
                    onClick={() => {
                      setConfigNodeId(node.id);
                      setConfigTarget(node.data.config?.target ?? "127.0.0.1");
                      setConfigProfile(node.data.config?.profile ?? "default");
                    }}
                  >
                    configure
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
              <select className="bg-slate-950 px-2 py-1" value={edgeBranch} onChange={(event) => setEdgeBranch(event.target.value as WorkflowEdge["branchCondition"])}>
                <option value="always">always</option>
                <option value="on_success">on_success</option>
                <option value="on_failure">on_failure</option>
              </select>
              <button
                type="button"
                className="spectra-button-primary px-2 py-1"
                onClick={() => {
                  addManualEdge(edgeSource, edgeTarget);
                  registerDemoAction("nodes_connected");
                }}
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

        <div className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-[0.2em] text-info">Execution Queue + Live Stream</h2>
          <p className="mt-2 text-xs text-slate-400">{statusMessage}</p>
          <div className="mt-3 rounded-lg border border-borderSubtle bg-slate-950/70 p-3">
            <ol className="space-y-2">
              {queue.map((nodeId, idx) => (
                <li key={nodeId} className="flex items-center justify-between rounded border border-borderSubtle px-2 py-2 text-sm">
                  <span>{idx + 1}. {nodes.find((node) => node.id === nodeId)?.data.label ?? nodeId}</span>
                  <div className="flex gap-1">
                    <button type="button" className="spectra-button-secondary px-2 py-0.5 text-xs" onClick={() => { moveQueueUp(nodeId); registerDemoAction("queue_reordered"); }}>up</button>
                    <button type="button" className="spectra-button-secondary px-2 py-0.5 text-xs" onClick={() => { moveQueueDown(nodeId); registerDemoAction("queue_reordered"); }}>down</button>
                    <button type="button" className="spectra-button-secondary px-2 py-0.5 text-xs" onClick={() => removeQueuedNode(nodeId)}>remove</button>
                  </div>
                </li>
              ))}
            </ol>
            <button type="button" className="spectra-button-primary mt-3 px-3 py-2 text-sm font-semibold" onClick={executeQueue}>
              Run Execution
            </button>
          </div>
        </div>

        <div className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-[0.2em] text-warning">Telemetry + Federation Diagnostics</h2>
          <div className="mt-3 flex gap-2">
            <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => { setActiveTab("logs"); registerDemoAction("logs_opened"); }}>Execution Logs</button>
            <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => { setActiveTab("telemetry"); registerDemoAction("telemetry_opened"); }}>Telemetry</button>
            <button type="button" className="spectra-button-secondary px-2 py-1 text-xs" onClick={() => { setActiveTab("signature"); registerDemoAction("signature_opened"); }}>Signature</button>
          </div>
          {activeTab === "logs" ? (
            <div className="mt-3 rounded border border-borderSubtle bg-slate-950/70 p-3">
              {telemetry.slice(0, 6).map((item) => (
                <pre key={item.event_id} className="spectra-mono mt-2 overflow-x-auto text-xs text-slate-200">{JSON.stringify(item, null, 2)}</pre>
              ))}
            </div>
          ) : null}
          {activeTab === "telemetry" ? (
            <div className="mt-3 rounded border border-borderSubtle bg-slate-950/70 p-3 text-xs">
              <p>Total events: {telemetry.length}</p>
              <p>Completed: {telemetry.filter((item) => item.status === "completed").length}</p>
              <p>Failed: {telemetry.filter((item) => item.status === "failed").length}</p>
            </div>
          ) : null}
          {activeTab === "signature" ? (
            <div className="mt-3 rounded border border-borderSubtle bg-slate-950/70 p-3">
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
          ) : null}
        </div>
      </article>

      {configNode ? (
        <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/50 p-4">
          <div className="spectra-panel w-full max-w-lg p-5">
            <h3 className="text-sm font-semibold text-white">Configure Wrapper: {configNode.data.label}</h3>
            <div className="mt-3 grid gap-3">
              <label className="text-sm">
                Target
                <input value={configTarget} onChange={(event) => setConfigTarget(event.target.value)} className="mt-1 w-full rounded border border-borderSubtle bg-slate-950 px-2 py-1" />
              </label>
              <label className="text-sm">
                Profile
                <input value={configProfile} onChange={(event) => setConfigProfile(event.target.value)} className="mt-1 w-full rounded border border-borderSubtle bg-slate-950 px-2 py-1" />
              </label>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                type="button"
                className="spectra-button-primary px-3 py-2 text-sm"
                onClick={() => {
                  updateNodeConfig(configNode.id, { target: configTarget, profile: configProfile });
                  registerDemoAction("wrapper_configured");
                  setConfigNodeId(null);
                }}
              >
                Save Config
              </button>
              <button type="button" className="spectra-button-secondary px-3 py-2 text-sm" onClick={() => setConfigNodeId(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
