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

import { afterEach, describe, expect, it, vi } from "vitest";

import { getNexusUrl, getVectorVueUrl } from "../../app/lib/cross-app-links";

describe("cross app link resolution", () => {
  afterEach(() => {
    delete process.env.VITE_NEXUS_URL;
    delete process.env.NEXT_PUBLIC_NEXUS_URL;
    delete process.env.UI_NEXUS_BASE_URL;
    delete process.env.VITE_VECTORVUE_URL;
    delete process.env.NEXT_PUBLIC_VECTORVUE_URL;
    delete process.env.UI_VECTORVUE_BASE_URL;
    vi.restoreAllMocks();
  });

  it("prefers explicit VITE env values", () => {
    process.env.VITE_NEXUS_URL = "https://nexus.test";
    process.env.VITE_VECTORVUE_URL = "https://vectorvue.test";
    expect(getNexusUrl()).toBe("https://nexus.test");
    expect(getVectorVueUrl()).toBe("https://vectorvue.test");
  });

  it("falls back to defaults and warns when env is missing", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(getNexusUrl()).toBe("http://localhost:3001");
    expect(getVectorVueUrl()).toBe("http://localhost:3002");
    expect(warnSpy).toHaveBeenCalledTimes(2);
  });
});
