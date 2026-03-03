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

export type ExecutionNodeType =
  | "initial_access"
  | "privilege_escalation"
  | "lateral_movement"
  | "exfiltration"
  | "c2";

export type ExecutionState = "queued" | "running" | "succeeded" | "failed";

export type WorkflowNode = {
  id: string;
  label: string;
  technique: string;
  nodeType: ExecutionNodeType;
};

export type WorkflowEdge = {
  id: string;
  sourceId: string;
  targetId: string;
  branchCondition: "always" | "on_success" | "on_failure";
};

export function defaultWorkflowGraph(): { nodes: WorkflowNode[]; edges: WorkflowEdge[] } {
  return {
    nodes: [
      { id: "n-initial", label: "Edge Access", technique: "T1133", nodeType: "initial_access" },
      { id: "n-priv", label: "Token Escalation", technique: "T1068", nodeType: "privilege_escalation" },
      { id: "n-lateral", label: "SMB Lateral", technique: "T1021.002", nodeType: "lateral_movement" },
      { id: "n-c2", label: "C2 Stabilize", technique: "T1071", nodeType: "c2" },
      { id: "n-exfil", label: "Data Staging", technique: "T1041", nodeType: "exfiltration" },
    ],
    edges: [
      { id: "e1", sourceId: "n-initial", targetId: "n-priv", branchCondition: "on_success" },
      { id: "e2", sourceId: "n-priv", targetId: "n-lateral", branchCondition: "on_success" },
      { id: "e3", sourceId: "n-lateral", targetId: "n-c2", branchCondition: "always" },
      { id: "e4", sourceId: "n-c2", targetId: "n-exfil", branchCondition: "on_success" },
    ],
  };
}

export function reorderNodes(nodes: WorkflowNode[], sourceId: string, targetId: string): WorkflowNode[] {
  if (sourceId === targetId) return [...nodes];
  const sourceIdx = nodes.findIndex((item) => item.id === sourceId);
  const targetIdx = nodes.findIndex((item) => item.id === targetId);
  if (sourceIdx < 0 || targetIdx < 0) return [...nodes];
  const next = [...nodes];
  const [moved] = next.splice(sourceIdx, 1);
  next.splice(targetIdx, 0, moved);
  return next;
}

export function executionOverlayByNode(
  nodes: WorkflowNode[],
  stateByTechnique: Record<string, ExecutionState>,
): Record<string, ExecutionState> {
  const overlay: Record<string, ExecutionState> = {};
  for (const node of nodes) {
    overlay[node.id] = stateByTechnique[node.technique] ?? "queued";
  }
  return overlay;
}

export function simulateConcurrentExecutionStates(nodes: WorkflowNode[], tick: number): Record<string, ExecutionState> {
  const statuses: ExecutionState[] = ["queued", "running", "succeeded", "failed"];
  const out: Record<string, ExecutionState> = {};
  nodes.forEach((node, idx) => {
    const state = statuses[(tick + idx) % statuses.length];
    out[node.technique] = state;
  });
  return out;
}

