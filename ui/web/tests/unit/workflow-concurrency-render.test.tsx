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
import { beforeEach, describe, expect, it, vi } from "vitest";

import { WorkflowWorkbench } from "../../app/components/workflow-workbench";

describe("Workflow concurrent execution rendering stress test", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve(
          new Response(
            JSON.stringify({
              items: [],
              nodes: [],
              edges: [],
              queue: [],
            }),
            { status: 200 }
          )
        )
      )
    );
    vi.stubGlobal(
      "EventSource",
      class {
        addEventListener() {}
        close() {}
      }
    );
  });

  it("renders key visualization panels and telemetry feed lines consistently", () => {
    render(<WorkflowWorkbench />);
    expect(screen.getByText(/Node-Link Execution Canvas/i)).toBeInTheDocument();
    expect(screen.getByText(/Execution Queue \+ Live Stream/i)).toBeInTheDocument();
    expect(screen.getByText(/Telemetry \+ Federation Diagnostics/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Execute Queue/i })).toBeInTheDocument();
  });
});
