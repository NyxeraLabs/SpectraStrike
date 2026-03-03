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

import { listRuntimeTasks, summarizeRuntimeQueue, upsertRuntimeTask } from "../../app/lib/execution-runtime-store";

describe("execution runtime store", () => {
  it("records and summarizes task queue states", () => {
    upsertRuntimeTask({
      task_id: "t-1",
      tool: "nmap",
      target: "127.0.0.1",
      status: "queued",
      retry_count: 0,
    });
    upsertRuntimeTask({
      task_id: "t-2",
      tool: "metasploit",
      target: "127.0.0.1",
      status: "retrying",
      retry_count: 1,
    });
    const rows = listRuntimeTasks(10);
    expect(rows.length).toBeGreaterThanOrEqual(2);
    const summary = summarizeRuntimeQueue();
    expect(summary.counts.queued).toBeGreaterThanOrEqual(1);
    expect(summary.counts.retrying).toBeGreaterThanOrEqual(1);
  });
});
