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

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";

import { WorkflowWorkbench } from "../../app/components/workflow-workbench";

describe("WorkflowWorkbench UI state consistency", () => {
  it("keeps independent interaction state across panels", async () => {
    const user = userEvent.setup();
    render(<WorkflowWorkbench />);

    await user.click(screen.getByTestId("heat-cell-TA0008-2"));
    expect(screen.getByText(/Selected TA0008 cell 3/i)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /\+ Privilege Lift/i }));
    expect(screen.getByTestId("playbook-list")).toHaveTextContent("Privilege Lift");

    expect(screen.getByText(/Selected TA0008 cell 3/i)).toBeInTheDocument();
  });
});
