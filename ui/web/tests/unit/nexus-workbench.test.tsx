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

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { NexusWorkbench } from "../../app/components/nexus-workbench";

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(""),
}));

describe("NexusWorkbench live surfaces", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (url.includes("/ui/api/execution/queue")) {
          return Promise.resolve(
            new Response(
              JSON.stringify({
                items: [
                  {
                    task_id: "task-1",
                    tool: "nmap",
                    target: "10.0.0.5",
                    status: "running",
                    retry_count: 1,
                    updated_at: "2026-03-03T14:01:00Z",
                  },
                ],
              }),
              { status: 200 },
            ),
          );
        }
        if (url.includes("/ui/api/telemetry/events")) {
          return Promise.resolve(
            new Response(
              JSON.stringify({
                items: [
                  {
                    event_id: "evt-1",
                    event_type: "wrapper_completed",
                    status: "completed",
                    target: "10.0.0.5",
                    timestamp: "2026-03-03T14:02:00Z",
                    envelope_id: "env-1",
                    signature_state: "verified",
                    vectorvue_response: "accepted",
                    attestation_proof: "sha256:abc",
                    retry_attempts: 0,
                  },
                ],
              }),
              { status: 200 },
            ),
          );
        }
        return Promise.resolve(new Response(JSON.stringify({ items: [] }), { status: 200 }));
      }),
    );
  });

  it("renders live feed and federation diagnostics from backend payloads", async () => {
    render(
      <NexusWorkbench
        tenantName="Acme Corp"
        tenantId="tenant-001"
        role="admin"
        vectorVueBaseUrl="https://vectorvue.local"
      />,
    );

    await waitFor(() => {
      expect(screen.getByText(/Live execution \+ telemetry feed loaded/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Execution task nmap/i)).toBeInTheDocument();
    expect(screen.getByText(/Telemetry wrapper_completed/i)).toBeInTheDocument();
    expect(screen.getByText(/Envelope ID: env-1/i)).toBeInTheDocument();
    expect(screen.getByText(/VectorVue response: accepted/i)).toBeInTheDocument();
  });
});
