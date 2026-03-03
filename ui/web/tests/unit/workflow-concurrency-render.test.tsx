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

import { WorkflowWorkbench } from "../../app/components/workflow-workbench";

describe("Workflow concurrent execution rendering stress test", () => {
  it("renders key visualization panels and telemetry feed lines consistently", () => {
    render(<WorkflowWorkbench />);
    expect(screen.getByText(/Node-Link Execution Canvas/i)).toBeInTheDocument();
    expect(screen.getByText(/Real-time Telemetry Streaming Panel/i)).toBeInTheDocument();
    expect(screen.getAllByTestId("telemetry-line").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByTestId("timeline-slider")).toBeInTheDocument();
  });
});

