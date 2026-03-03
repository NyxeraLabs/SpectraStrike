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

import { beforeEach, describe, expect, it } from "vitest";

import { useWorkflowStore } from "../../app/lib/workflow-store";

describe("workflow store state transitions", () => {
  beforeEach(() => {
    useWorkflowStore.setState({
      nodes: [],
      edges: [],
      queue: [],
      wrappers: [],
      telemetry: [],
      executionStatus: {},
      statusMessage: "Loading playbook...",
      edgeBranch: "always",
      spectraDemoActive: false,
      spectraDemoStep: "intro",
    });
  });

  it("supports node add/remove, edge linking, and queue reorder", () => {
    const state = useWorkflowStore.getState();
    state.addPrivilegeLiftNode();

    const firstNode = useWorkflowStore.getState().nodes[0];
    expect(firstNode.data.label).toBe("Privilege Lift");

    useWorkflowStore.getState().duplicateNode(firstNode.id);
    const duplicated = useWorkflowStore.getState().nodes.find((node) => node.id !== firstNode.id);
    expect(duplicated).toBeDefined();

    useWorkflowStore.getState().setEdgeBranch("on_success");
    useWorkflowStore.getState().addManualEdge(firstNode.id, duplicated!.id);
    expect(useWorkflowStore.getState().edges).toHaveLength(1);
    expect(useWorkflowStore.getState().edges[0].data?.branchCondition).toBe("on_success");

    useWorkflowStore.getState().queueNode(firstNode.id);
    useWorkflowStore.getState().queueNode(duplicated!.id);
    useWorkflowStore.getState().moveQueueUp(duplicated!.id);
    expect(useWorkflowStore.getState().queue).toEqual([duplicated!.id, firstNode.id]);

    useWorkflowStore.getState().removeNode(firstNode.id);
    expect(useWorkflowStore.getState().nodes.some((node) => node.id === firstNode.id)).toBe(false);
    expect(useWorkflowStore.getState().queue.includes(firstNode.id)).toBe(false);
  });
});
