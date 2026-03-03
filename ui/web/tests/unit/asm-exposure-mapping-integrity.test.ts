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
  defaultAsmGraph,
  exposureGraphToPlaybookActions,
  validateExposureMappings,
} from "../../app/lib/asm-graph";

describe("ASM exposure mapping integrity validation", () => {
  it("keeps mapping coverage and deterministic playbook conversion", () => {
    const graph = defaultAsmGraph();
    const coverage = validateExposureMappings(graph.exposures, graph.nodes);

    expect(coverage.missingAssets).toEqual([]);
    expect(coverage.coverageRatio).toBeGreaterThan(0.5);

    const actions = exposureGraphToPlaybookActions(graph.exposures);
    expect(actions.length).toBe(graph.exposures.length);
    expect(actions[0]).toContain("severity:0.84");
  });
});
