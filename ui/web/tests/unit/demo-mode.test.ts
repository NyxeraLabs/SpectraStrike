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

import { describe, expect, it } from "vitest";

import {
  buildNexusDemoUrl,
  NEXUS_DEMO_STEPS,
  nextDemoStep,
  SPECTRA_DEMO_STEPS,
  buildVectorVueDemoUrl,
  isDemoQuery,
  shouldStartSpectraDemo,
  VECTORVUE_DEMO_STEPS,
} from "../../app/lib/demo-mode";

describe("demo mode contracts", () => {
  it("starts demo only when onboard flag is absent", () => {
    const missing = { getItem: () => null } as Storage;
    const done = { getItem: () => "true" } as Storage;
    expect(shouldStartSpectraDemo(missing)).toBe(true);
    expect(shouldStartSpectraDemo(done)).toBe(false);
  });

  it("builds explicit cross-app demo URLs", () => {
    expect(buildNexusDemoUrl()).toContain("demo=true&source=spectrastrike");
    expect(buildVectorVueDemoUrl()).toContain("/portal/validation?demo=true&source=nexus");
  });

  it("parses demo query flag", () => {
    expect(isDemoQuery("?demo=true&source=spectrastrike")).toBe(true);
    expect(isDemoQuery("?source=spectrastrike")).toBe(false);
  });

  it("advances demo state machines deterministically", () => {
    expect(nextDemoStep(SPECTRA_DEMO_STEPS, "intro")).toBe("canvas_intro");
    expect(nextDemoStep(NEXUS_DEMO_STEPS, "open_vectorvue")).toBe("complete");
    expect(nextDemoStep(VECTORVUE_DEMO_STEPS, "complete")).toBe("complete");
  });
});
