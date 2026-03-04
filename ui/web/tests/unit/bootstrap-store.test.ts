import { describe, expect, it } from "vitest";

import {
  applyBootstrapSetup,
  getBootstrapZeroStatus,
  resetBootstrapState,
} from "../../app/lib/bootstrap-store";

describe("first-run DB-zero detection and setup wizard state", () => {
  it("reports DB-zero when bootstrap state is empty", () => {
    resetBootstrapState();
    const status = getBootstrapZeroStatus(0);
    expect(status.is_db_zero).toBe(true);
  });

  it("marks environment configured after setup", () => {
    resetBootstrapState();
    applyBootstrapSetup({
      workspaceName: "acme",
      wrappers: ["nmap", "metasploit"],
      federationEndpoint: "http://localhost:8000",
    });
    const status = getBootstrapZeroStatus(1);
    expect(status.is_db_zero).toBe(false);
    expect(status.platform_onboarded).toBe(true);
    expect(status.wrapper_configured).toBe(2);
  });
});
