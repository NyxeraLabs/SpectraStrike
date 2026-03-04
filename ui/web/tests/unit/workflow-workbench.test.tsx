/*
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
*/

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("reactflow", () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="reactflow-mock">{children}</div>,
  Background: () => null,
  Controls: () => null,
  MiniMap: () => null,
}));

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
                items: [
                  { key: "nmap", label: "Nmap", category: "recon", nodeType: "initial_access", description: "scan" },
                ],
              }),
              { status: 200 },
            ),
          );
        }
        if (url.includes("/ui/api/bootstrap/status")) {
          return Promise.resolve(
            new Response(
              JSON.stringify({
                status: {
                  users: 1,
                  tenants: 1,
                  keys: 1,
                  wrapper_configured: 1,
                  federation_configured: 1,
                  is_db_zero: false,
                  platform_onboarded: true,
                },
              }),
              { status: 200 },
            ),
          );
        }
        if (url.includes("/ui/api/execution/playbook")) {
          return Promise.resolve(new Response(JSON.stringify({ nodes: [], edges: [], queue: [] }), { status: 200 }));
        }
        return Promise.resolve(new Response(JSON.stringify({ items: [] }), { status: 200 }));
      }),
    );
    vi.stubGlobal(
      "EventSource",
      class {
        addEventListener() {}
        close() {}
      },
    );
    Object.defineProperty(document.documentElement, "requestFullscreen", {
      value: vi.fn(() => Promise.resolve()),
      configurable: true,
    });
  });

  it("supports adding wrappers via picker", async () => {
    const user = userEvent.setup();
    render(<WorkflowWorkbench />);

    await user.click(await screen.findByRole("button", { name: /Nmap/i }));
    await waitFor(() => {
      expect(screen.getByTestId("playbook-list")).toHaveTextContent("Nmap");
    });
  });

  it("renders campaign selector with seeded tenant options", async () => {
    render(<WorkflowWorkbench />);
    const selector = await screen.findByLabelText(/Active Campaign/i);
    expect(selector).toHaveValue("10000000-0000-0000-0000-000000000001");
    expect(screen.getByRole("option", { name: /ACME Campaign/i })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /Globex Campaign/i })).toBeInTheDocument();
  });

  it("requests fullscreen API and applies true fullscreen mode", async () => {
    const user = userEvent.setup();
    render(<WorkflowWorkbench />);

    await user.click(screen.getByRole("button", { name: /Full Screen/i }));
    expect(document.documentElement.requestFullscreen).toHaveBeenCalledTimes(1);
  });
});
