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

// @vitest-environment node

import { describe, expect, it } from "vitest";

import { authenticateUser, issueSessionToken, isSessionTokenValid, registerUser } from "../../app/lib/auth-store";

describe("auth-store", () => {
  it("registers and authenticates a user", async () => {
    const username = `unit_user_${Date.now()}`;
    const password = "Strong!Password123";
    await registerUser({
      username,
      fullName: "Unit Test User",
      email: `${username}@example.test`,
      password,
      acceptedPoliciesAt: new Date().toISOString(),
    });

    const authenticated = await authenticateUser(username, password);
    expect(authenticated).not.toBeNull();
    expect(authenticated?.username).toBe(username);
  });

  it("issues valid session token", () => {
    const issued = issueSessionToken("usr-test-session");
    expect(issued.accessToken.length).toBeGreaterThan(20);
    expect(isSessionTokenValid(issued.accessToken)).toBe(true);
  });
});

