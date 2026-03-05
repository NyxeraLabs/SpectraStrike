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
  dequeueNode,
  enqueueNode,
  executionOverlayByNode,
  reorderQueue,
  reorderNodes,
  simulateConcurrentExecutionStates,
  type WorkflowNode,
} from "../../app/lib/workflow-graph";

describe("Workflow graph execution state validation", () => {
  it("maps execution states to graph overlays and preserves reorder semantics", () => {
    const graph: WorkflowNode[] = [
      { id: "n1", label: "Recon", technique: "T1595", nodeType: "initial_access" },
      { id: "n2", label: "Esc", technique: "T1068", nodeType: "privilege_escalation" },
      { id: "n3", label: "Move", technique: "T1021.002", nodeType: "lateral_movement" },
    ];
    const first = graph[0];
    const third = graph[2];
    const reordered = reorderNodes(graph, first.id, third.id);
    expect(reordered[2].id).toBe(first.id);

    const stateByTechnique = simulateConcurrentExecutionStates(reordered, 2);
    const overlay = executionOverlayByNode(reordered, stateByTechnique);
    expect(Object.keys(overlay).length).toBe(reordered.length);
    expect(overlay[reordered[0].id]).toBeDefined();
  });

  it("supports queue add/remove/reorder operations", () => {
    const queue = enqueueNode([], "n1");
    expect(queue).toEqual(["n1"]);
    const withSecond = enqueueNode(queue, "n2");
    expect(withSecond).toEqual(["n1", "n2"]);
    const reordered = reorderQueue(withSecond, "n2", "n1");
    expect(reordered).toEqual(["n2", "n1"]);
    const removed = dequeueNode(reordered, "n2");
    expect(removed).toEqual(["n1"]);
  });
});
