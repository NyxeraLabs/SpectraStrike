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
  defaultWorkflowGraph,
  executionOverlayByNode,
  reorderNodes,
  simulateConcurrentExecutionStates,
} from "../../app/lib/workflow-graph";

describe("Workflow graph execution state validation", () => {
  it("maps execution states to graph overlays and preserves reorder semantics", () => {
    const graph = defaultWorkflowGraph();
    const first = graph.nodes[0];
    const third = graph.nodes[2];
    const reordered = reorderNodes(graph.nodes, first.id, third.id);
    expect(reordered[2].id).toBe(first.id);

    const stateByTechnique = simulateConcurrentExecutionStates(reordered, 2);
    const overlay = executionOverlayByNode(reordered, stateByTechnique);
    expect(Object.keys(overlay).length).toBe(reordered.length);
    expect(overlay[reordered[0].id]).toBeDefined();
  });
});

