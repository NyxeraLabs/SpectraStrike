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
});
