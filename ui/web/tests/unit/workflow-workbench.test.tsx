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
import { beforeEach, describe, expect, it, vi } from "vitest";

import { WorkflowWorkbench } from "../../app/components/workflow-workbench";

describe("WorkflowWorkbench UI state consistency", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.includes("/ui/api/execution/wrappers")) {
          return Promise.resolve(
            new Response(
              JSON.stringify({
                items: [{ key: "nmap", label: "Nmap", category: "recon", nodeType: "initial_access", description: "scan" }],
              }),
              { status: 200 }
            )
          );
        }
        if (url.includes("/ui/api/execution/playbook")) {
          return Promise.resolve(
            new Response(JSON.stringify({ nodes: [], edges: [], queue: [] }), { status: 200 })
          );
        }
        return Promise.resolve(new Response(JSON.stringify({ items: [] }), { status: 200 }));
      })
    );
    vi.stubGlobal(
      "EventSource",
      class {
        addEventListener() {}
        close() {}
      }
    );
  });

  it("supports adding wrappers and persists list state", async () => {
    const user = userEvent.setup();
    render(<WorkflowWorkbench />);

    await user.click(screen.getByRole("button", { name: /\+ Privilege Lift/i }));
    expect(screen.getByTestId("playbook-list")).toHaveTextContent("Privilege Lift");
  });
});
