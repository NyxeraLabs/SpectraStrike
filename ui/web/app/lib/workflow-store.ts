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

import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type Node,
  type NodeChange,
} from "reactflow";
import { create } from "zustand";

import {
  canAdvanceSpectraStep,
  nextDemoStep,
  SPECTRA_DEMO_STEPS,
  type SpectraDemoAction,
  type SpectraDemoStep,
} from "./demo-mode";
import {
  defaultWorkflowGraph,
  dequeueNode,
  enqueueNode,
  reorderQueue,
  type RuntimeExecutionState,
  type WorkflowEdge,
  type WorkflowNode,
} from "./workflow-graph";
import type { WrapperDescriptor } from "./wrapper-registry";

export type TelemetryEvent = {
  event_id: string;
  source: string;
  status: string;
  event_type: string;
  actor: string;
  target: string;
  timestamp: string;
  envelope_id?: string;
  signature_state?: string;
  attestation_proof?: string;
  retry_attempts?: number;
  failure_reason?: string;
  vectorvue_response?: string;
  raw_output?: string;
  parsed_findings?: unknown;
};

export type FlowNodeData = {
  label: string;
  technique: string;
  nodeType: WorkflowNode["nodeType"];
  wrapperKey?: string;
  config?: {
    target?: string;
    profile?: string;
  };
};

export type FlowEdgeData = {
  branchCondition: WorkflowEdge["branchCondition"];
};

export type FlowNode = Node<FlowNodeData>;
export type FlowEdge = Edge<FlowEdgeData>;

type WorkflowStoreState = {
  nodes: FlowNode[];
  edges: FlowEdge[];
  queue: string[];
  wrappers: WrapperDescriptor[];
  telemetry: TelemetryEvent[];
  executionStatus: Record<string, RuntimeExecutionState>;
  statusMessage: string;
  edgeBranch: WorkflowEdge["branchCondition"];
  spectraDemoActive: boolean;
  spectraDemoStep: SpectraDemoStep;
  completedDemoActions: SpectraDemoAction[];
  setFromBackend: (payload: { nodes: WorkflowNode[]; edges: WorkflowEdge[]; queue: string[] }) => void;
  setWrappers: (wrappers: WrapperDescriptor[]) => void;
  setTelemetry: (items: TelemetryEvent[]) => void;
  setExecutionStatus: (
    status:
      | Record<string, RuntimeExecutionState>
      | ((prev: Record<string, RuntimeExecutionState>) => Record<string, RuntimeExecutionState>)
  ) => void;
  setStatusMessage: (message: string) => void;
  setEdgeBranch: (branch: WorkflowEdge["branchCondition"]) => void;
  seedDemoPlaybook: () => void;
  nextDemoStep: () => void;
  registerDemoAction: (action: SpectraDemoAction) => void;
  dismissDemo: () => void;
  enableDemo: () => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addWrapperNode: (wrapper: WrapperDescriptor) => void;
  addWrapperNodeAt: (wrapper: WrapperDescriptor, x: number, y: number) => void;
  updateNodeConfig: (nodeId: string, config: NonNullable<FlowNodeData["config"]>) => void;
  addPrivilegeLiftNode: () => void;
  duplicateNode: (nodeId: string) => void;
  removeNode: (nodeId: string) => void;
  removeNodes: (nodeIds: string[]) => void;
  queueNode: (nodeId: string) => void;
  removeQueuedNode: (nodeId: string) => void;
  moveQueueUp: (nodeId: string) => void;
  moveQueueDown: (nodeId: string) => void;
  addManualEdge: (sourceId: string, targetId: string) => void;
  removeEdge: (edgeId: string) => void;
  getPersistencePayload: () => { nodes: WorkflowNode[]; edges: WorkflowEdge[]; queue: string[] };
};

function defaultPosition(index: number): { x: number; y: number } {
  const row = Math.floor(index / 4);
  const col = index % 4;
  return { x: 80 + col * 240, y: 80 + row * 160 };
}

function graphToFlowNodes(nodes: WorkflowNode[]): FlowNode[] {
  return nodes.map((node, index) => ({
    id: node.id,
    position: defaultPosition(index),
    data: {
      label: node.label,
      technique: node.technique,
      nodeType: node.nodeType,
      wrapperKey: node.wrapperKey,
    },
    type: "default",
  }));
}

function graphToFlowEdges(edges: WorkflowEdge[]): FlowEdge[] {
  return edges.map((edge) => ({
    id: edge.id,
    source: edge.sourceId,
    target: edge.targetId,
    label: edge.branchCondition,
    data: { branchCondition: edge.branchCondition },
    type: "default",
    animated: false,
  }));
}

function flowToGraphNodes(nodes: FlowNode[]): WorkflowNode[] {
  return nodes.map((node) => ({
    id: node.id,
    label: node.data.label,
    technique: node.data.technique,
    nodeType: node.data.nodeType,
    wrapperKey: node.data.wrapperKey,
  }));
}

function flowToGraphEdges(edges: FlowEdge[]): WorkflowEdge[] {
  return edges.map((edge) => ({
    id: edge.id,
    sourceId: edge.source,
    targetId: edge.target,
    branchCondition: edge.data?.branchCondition ?? "always",
  }));
}

function addWrapper(state: WorkflowStoreState, wrapper: WrapperDescriptor, position?: { x: number; y: number }) {
  return {
    nodes: [
      ...state.nodes,
      {
        id: `n-${Date.now()}-${wrapper.key}`,
        position: position ?? defaultPosition(state.nodes.length),
        data: {
          label: wrapper.label,
          technique: "T0000",
          nodeType: wrapper.nodeType,
          wrapperKey: wrapper.key,
          config: {
            profile: "default",
            target: "127.0.0.1",
          },
        },
        type: "default",
      },
    ],
  };
}

const defaultGraph = defaultWorkflowGraph();

export const useWorkflowStore = create<WorkflowStoreState>((set, get) => ({
  nodes: graphToFlowNodes(defaultGraph.nodes),
  edges: graphToFlowEdges(defaultGraph.edges),
  queue: [],
  wrappers: [],
  telemetry: [],
  executionStatus: {},
  statusMessage: "Loading playbook...",
  edgeBranch: "always",
  spectraDemoActive: false,
  spectraDemoStep: "welcome",
  completedDemoActions: [],

  setFromBackend: (payload) =>
    set({
      nodes: graphToFlowNodes(payload.nodes),
      edges: graphToFlowEdges(payload.edges),
      queue: payload.queue,
    }),
  setWrappers: (wrappers) => set({ wrappers }),
  setTelemetry: (telemetry) => set({ telemetry }),
  setExecutionStatus: (status) =>
    set((state) => ({
      executionStatus: typeof status === "function" ? status(state.executionStatus) : status,
    })),
  setStatusMessage: (statusMessage) => set({ statusMessage }),
  setEdgeBranch: (edgeBranch) => set({ edgeBranch }),

  enableDemo: () =>
    set({
      spectraDemoActive: true,
      spectraDemoStep: "welcome",
      completedDemoActions: [],
    }),
  seedDemoPlaybook: () =>
    set({
      nodes: graphToFlowNodes([]),
      edges: graphToFlowEdges([]),
      queue: [],
    }),
  nextDemoStep: () =>
    set((state) => ({
      spectraDemoStep: nextDemoStep(SPECTRA_DEMO_STEPS, state.spectraDemoStep),
    })),
  registerDemoAction: (action) =>
    set((state) => {
      if (!canAdvanceSpectraStep(state.spectraDemoStep, action)) {
        return {
          completedDemoActions: [...state.completedDemoActions, action],
        };
      }
      return {
        completedDemoActions: [...state.completedDemoActions, action],
        spectraDemoStep: nextDemoStep(SPECTRA_DEMO_STEPS, state.spectraDemoStep),
      };
    }),
  dismissDemo: () =>
    set({
      spectraDemoActive: false,
      spectraDemoStep: "complete",
    }),

  onNodesChange: (changes) =>
    set((state) => ({
      nodes: applyNodeChanges(changes, state.nodes),
    })),
  onEdgesChange: (changes) =>
    set((state) => ({
      edges: applyEdgeChanges(changes, state.edges),
    })),
  onConnect: (connection) =>
    set((state) => {
      const edge: FlowEdge = {
        id: `e-${Date.now()}`,
        source: connection.source ?? "",
        target: connection.target ?? "",
        label: state.edgeBranch,
        data: { branchCondition: state.edgeBranch },
      };
      return {
        edges: addEdge(edge, state.edges),
      };
    }),

  addWrapperNode: (wrapper) => set((state) => addWrapper(state, wrapper)),
  addWrapperNodeAt: (wrapper, x, y) => set((state) => addWrapper(state, wrapper, { x, y })),
  updateNodeConfig: (nodeId, config) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: {
                ...node.data,
                config,
              },
            }
          : node,
      ),
    })),
  addPrivilegeLiftNode: () =>
    set((state) => ({
      nodes: [
        ...state.nodes,
        {
          id: `n-${Date.now()}-priv-lift`,
          position: defaultPosition(state.nodes.length),
          data: {
            label: "Privilege Lift",
            technique: "T1068",
            nodeType: "privilege_escalation",
            wrapperKey: "metasploit",
            config: {
              profile: "priv-lift",
              target: "127.0.0.1",
            },
          },
          type: "default",
        },
      ],
    })),
  duplicateNode: (nodeId) =>
    set((state) => {
      const node = state.nodes.find((item) => item.id === nodeId);
      if (!node) return {};
      return {
        nodes: [
          ...state.nodes,
          {
            ...node,
            id: `copy-${Date.now()}-${nodeId}`,
            position: { x: node.position.x + 40, y: node.position.y + 40 },
          },
        ],
      };
    }),
  removeNode: (nodeId) =>
    set((state) => ({
      nodes: state.nodes.filter((item) => item.id !== nodeId),
      edges: state.edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId),
      queue: dequeueNode(state.queue, nodeId),
    })),
  removeNodes: (nodeIds) =>
    set((state) => {
      const toRemove = new Set(nodeIds);
      return {
        nodes: state.nodes.filter((item) => !toRemove.has(item.id)),
        edges: state.edges.filter((edge) => !toRemove.has(edge.source) && !toRemove.has(edge.target)),
        queue: state.queue.filter((nodeId) => !toRemove.has(nodeId)),
      };
    }),
  queueNode: (nodeId) =>
    set((state) => ({
      queue: enqueueNode(state.queue, nodeId),
    })),
  removeQueuedNode: (nodeId) =>
    set((state) => ({
      queue: dequeueNode(state.queue, nodeId),
    })),
  moveQueueUp: (nodeId) =>
    set((state) => {
      const index = state.queue.indexOf(nodeId);
      if (index <= 0) return {};
      return {
        queue: reorderQueue(state.queue, nodeId, state.queue[index - 1]),
      };
    }),
  moveQueueDown: (nodeId) =>
    set((state) => {
      const index = state.queue.indexOf(nodeId);
      if (index < 0 || index + 1 >= state.queue.length) return {};
      return {
        queue: reorderQueue(state.queue, nodeId, state.queue[index + 1]),
      };
    }),
  addManualEdge: (sourceId, targetId) =>
    set((state) => {
      if (!sourceId || !targetId || sourceId === targetId) {
        return {};
      }
      const exists = state.edges.some((edge) => edge.source === sourceId && edge.target === targetId);
      if (exists) {
        return {};
      }
      const edge: FlowEdge = {
        id: `manual-${Date.now()}-${sourceId}-${targetId}`,
        source: sourceId,
        target: targetId,
        data: { branchCondition: state.edgeBranch },
        label: state.edgeBranch,
      };
      return {
        edges: [...state.edges, edge],
      };
    }),
  removeEdge: (edgeId) =>
    set((state) => ({
      edges: state.edges.filter((edge) => edge.id !== edgeId),
    })),
  getPersistencePayload: () => {
    const state = get();
    return {
      nodes: flowToGraphNodes(state.nodes),
      edges: flowToGraphEdges(state.edges),
      queue: [...state.queue],
    };
  },
}));
