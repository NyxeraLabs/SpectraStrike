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
  buildExecutionActivities,
  buildFederationDiagnostics,
  buildTelemetryActivities,
  buildNexusContext,
  buildVectorVueDeepLink,
  canAccessNexusArea,
  decodeNexusContext,
  encodeNexusContext,
} from "../../app/lib/nexus-context";

describe("Nexus cross-module state synchronization", () => {
  it("encodes and decodes shared context deterministically for VectorVue deep links", () => {
    const context = buildNexusContext({
      tenantId: "tenant-001",
      tenantName: "Acme Corp",
      role: "auditor",
      campaignId: "cmp-42",
      findingId: "f-9001",
      ts: "2026-03-03T14:00:00Z",
    });

    const query = encodeNexusContext(context);
    const decoded = decodeNexusContext(query);
    expect(decoded).toEqual(context);

    const link = buildVectorVueDeepLink("https://vectorvue.local", context);
    expect(link).toContain("/portal/nexus?");
    expect(link).toContain("tenant_id=tenant-001");
    expect(canAccessNexusArea("auditor", "export")).toBe(true);
    expect(canAccessNexusArea("operator", "export")).toBe(false);
  });

  it("maps live execution and telemetry payloads into feed + diagnostics views", () => {
    const executionFeed = buildExecutionActivities([
      {
        task_id: "task-1",
        tool: "nmap",
        target: "10.0.0.5",
        status: "running",
        retry_count: 1,
        updated_at: "2026-03-03T14:01:00Z",
      },
    ]);
    expect(executionFeed[0].title).toContain("Execution task nmap");
    expect(executionFeed[0].type).toBe("execution");

    const telemetryFeed = buildTelemetryActivities([
      {
        event_id: "evt-1",
        event_type: "wrapper_completed",
        status: "completed",
        target: "10.0.0.5",
        timestamp: "2026-03-03T14:02:00Z",
        envelope_id: "env-1",
        signature_state: "verified",
        vectorvue_response: "accepted",
      },
    ]);
    expect(telemetryFeed[0].source).toBe("vectorvue");
    expect(telemetryFeed[0].type).toBe("assurance");

    const diagnostics = buildFederationDiagnostics([
      {
        envelope_id: "env-1",
        signature_state: "verified",
        failure_reason: "",
        retry_attempts: 0,
        vectorvue_response: "accepted",
        attestation_proof: "sha256:abc",
        timestamp: "2026-03-03T14:02:00Z",
      },
    ]);
    expect(diagnostics[0].envelopeId).toBe("env-1");
    expect(diagnostics[0].vectorVueResponse).toBe("accepted");
  });
});
