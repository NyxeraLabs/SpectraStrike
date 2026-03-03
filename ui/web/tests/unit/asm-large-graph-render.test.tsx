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

import React from "react";
import { render, screen } from "@testing-library/react";

import { AsmWorkbench } from "../../app/components/asm-workbench";
import { buildLargeAsmGraph } from "../../app/lib/asm-graph";

describe("ASM large graph rendering performance test", () => {
  it("renders a large asset list with stable key panels", () => {
    const large = buildLargeAsmGraph(220);
    render(<AsmWorkbench initialNodes={large.nodes} />);

    expect(screen.getByText(/Asset Graph Visualization Engine/i)).toBeInTheDocument();
    expect(screen.getByTestId("asm-builder")).toBeInTheDocument();
    expect(screen.getByTestId("playbook-convert")).toBeInTheDocument();
    expect(screen.getAllByTestId(/^asm-list-/).length).toBe(220);
  });
});
