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
  accessibilityChecklist,
  keyboardShortcutTarget,
  reduceRenderBudget,
  roleCanExport,
} from "../../app/lib/global-ui";

describe("Global UI accessibility and rendering performance", () => {
  it("keeps baseline WCAG checks and keyboard shortcut mappings", () => {
    const checks = accessibilityChecklist();
    expect(checks.length).toBeGreaterThanOrEqual(4);
    expect(checks.every((item) => item.status === "pass")).toBe(true);

    expect(keyboardShortcutTarget("1", true)).toBe("/dashboard");
    expect(keyboardShortcutTarget("4", true)).toBe("/dashboard/telemetry");
    expect(keyboardShortcutTarget("4", false)).toBeNull();

    expect(roleCanExport("auditor")).toBe(true);
    expect(roleCanExport("red_team")).toBe(false);
  });

  it("applies rendering budget for large notification/activity lists", () => {
    const rows = Array.from({ length: 2000 }, (_value, idx) => ({ id: idx + 1 }));
    const started = Date.now();
    const reduced = reduceRenderBudget(rows, 180);
    const elapsed = Date.now() - started;

    expect(reduced.length).toBe(180);
    expect(elapsed).toBeLessThan(200);
  });
});
