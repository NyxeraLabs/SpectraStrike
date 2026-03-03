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

import {
  reorderNodes,
  type WorkflowNode,
  type WorkflowEdge,
} from "./workflow-graph";

export type AsmNodeType = "external" | "internal" | "cloud_identity" | "service";

export type AsmNode = {
  id: string;
  label: string;
  nodeType: AsmNodeType;
  riskScore: number;
};

export type AsmEdge = {
  id: string;
  sourceId: string;
  targetId: string;
  relation: "owns" | "exposes" | "vuln_path" | "pivot" | "iam_assume_role";
};

export type ExposureMapping = {
  assetId: string;
  exposureId: string;
  severity: number;
  technique: string;
};

export function defaultAsmGraph(): { nodes: AsmNode[]; edges: AsmEdge[]; exposures: ExposureMapping[] } {
  return {
    nodes: [
      { id: "internet", label: "Internet Edge", nodeType: "external", riskScore: 0.88 },
      { id: "vpn-gw", label: "VPN Gateway", nodeType: "external", riskScore: 0.77 },
      { id: "web-app", label: "Web App Cluster", nodeType: "service", riskScore: 0.69 },
      { id: "core-db", label: "Core Database", nodeType: "internal", riskScore: 0.61 },
      { id: "aws-role", label: "AWS Build Role", nodeType: "cloud_identity", riskScore: 0.56 },
    ],
    edges: [
      { id: "a1", sourceId: "internet", targetId: "vpn-gw", relation: "exposes" },
      { id: "a2", sourceId: "vpn-gw", targetId: "web-app", relation: "pivot" },
      { id: "a3", sourceId: "web-app", targetId: "core-db", relation: "vuln_path" },
      { id: "a4", sourceId: "web-app", targetId: "aws-role", relation: "iam_assume_role" },
    ],
    exposures: [
      { assetId: "vpn-gw", exposureId: "exp-vpn-ssl", severity: 0.84, technique: "T1133" },
      { assetId: "web-app", exposureId: "exp-web-rce", severity: 0.79, technique: "T1190" },
      { assetId: "core-db", exposureId: "exp-db-creds", severity: 0.63, technique: "T1552" },
    ],
  };
}

function asmToWorkflowNodes(nodes: AsmNode[]): WorkflowNode[] {
  return nodes.map((node) => ({
    id: node.id,
    label: node.label,
    technique: `ASM-${node.id}`,
    nodeType: "lateral_movement",
  }));
}

function workflowToAsmNodes(next: WorkflowNode[], base: AsmNode[]): AsmNode[] {
  const byId = new Map(base.map((node) => [node.id, node]));
  return next
    .map((item) => byId.get(item.id))
    .filter((item): item is AsmNode => Boolean(item));
}

// Reuses shared graph-core reordering utility to keep drag behavior consistent.
export function reorderAsmNodes(nodes: AsmNode[], sourceId: string, targetId: string): AsmNode[] {
  const mapped = asmToWorkflowNodes(nodes);
  const reordered = reorderNodes(mapped, sourceId, targetId);
  return workflowToAsmNodes(reordered, nodes);
}

export function riskOverlayByAsset(nodes: AsmNode[]): Record<string, "low" | "medium" | "high" | "critical"> {
  const overlay: Record<string, "low" | "medium" | "high" | "critical"> = {};
  nodes.forEach((node) => {
    if (node.riskScore >= 0.8) {
      overlay[node.id] = "critical";
    } else if (node.riskScore >= 0.65) {
      overlay[node.id] = "high";
    } else if (node.riskScore >= 0.45) {
      overlay[node.id] = "medium";
    } else {
      overlay[node.id] = "low";
    }
  });
  return overlay;
}

export function buildLargeAsmGraph(size: number): { nodes: AsmNode[]; edges: AsmEdge[] } {
  const nodeCount = Math.max(2, size);
  const nodes: AsmNode[] = [];
  const edges: AsmEdge[] = [];
  for (let i = 0; i < nodeCount; i += 1) {
    nodes.push({
      id: `asset-${i}`,
      label: `Asset ${i}`,
      nodeType: i % 4 === 0 ? "external" : i % 4 === 1 ? "service" : i % 4 === 2 ? "internal" : "cloud_identity",
      riskScore: ((i % 10) + 1) / 10,
    });
    if (i > 0) {
      edges.push({
        id: `edge-${i - 1}-${i}`,
        sourceId: `asset-${i - 1}`,
        targetId: `asset-${i}`,
        relation: i % 3 === 0 ? "pivot" : "exposes",
      });
    }
  }
  return { nodes, edges };
}

export function validateExposureMappings(
  mappings: ExposureMapping[],
  nodes: AsmNode[],
): { missingAssets: string[]; coverageRatio: number } {
  const assets = new Set(nodes.map((node) => node.id));
  const missingAssets = mappings
    .filter((mapping) => !assets.has(mapping.assetId))
    .map((mapping) => mapping.assetId);
  const covered = new Set(mappings.filter((mapping) => assets.has(mapping.assetId)).map((mapping) => mapping.assetId));
  const coverageRatio = nodes.length === 0 ? 1 : covered.size / nodes.length;
  return { missingAssets, coverageRatio };
}

export function exposureGraphToPlaybookActions(mappings: ExposureMapping[]): string[] {
  return mappings
    .sort((a, b) => b.severity - a.severity)
    .map(
      (mapping, idx) =>
        `${idx + 1}. Validate ${mapping.assetId} via ${mapping.technique} (source:${mapping.exposureId}, severity:${mapping.severity.toFixed(2)})`,
    );
}

export function edgeCountsByRelation(edges: AsmEdge[]): Record<AsmEdge["relation"], number> {
  const counts: Record<AsmEdge["relation"], number> = {
    owns: 0,
    exposes: 0,
    vuln_path: 0,
    pivot: 0,
    iam_assume_role: 0,
  };
  edges.forEach((edge) => {
    counts[edge.relation] += 1;
  });
  return counts;
}

export function asWorkflowEdges(edges: AsmEdge[]): WorkflowEdge[] {
  return edges.map((edge) => ({
    id: edge.id,
    sourceId: edge.sourceId,
    targetId: edge.targetId,
    branchCondition: edge.relation === "pivot" ? "on_success" : "always",
  }));
}
