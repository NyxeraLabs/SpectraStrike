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

import type { RuntimeExecutionState } from "./workflow-graph";

export type RuntimeTask = {
  task_id: string;
  tool: string;
  target: string;
  status: RuntimeExecutionState;
  retry_count: number;
  created_at: string;
  updated_at: string;
};

const tasks: RuntimeTask[] = [];

function nowIso(): string {
  return new Date().toISOString();
}

export function upsertRuntimeTask(task: Omit<RuntimeTask, "created_at" | "updated_at"> & { created_at?: string }): RuntimeTask {
  const existing = tasks.find((item) => item.task_id === task.task_id);
  if (existing) {
    existing.tool = task.tool;
    existing.target = task.target;
    existing.status = task.status;
    existing.retry_count = task.retry_count;
    existing.updated_at = nowIso();
    return existing;
  }
  const created: RuntimeTask = {
    ...task,
    created_at: task.created_at ?? nowIso(),
    updated_at: nowIso(),
  };
  tasks.unshift(created);
  return created;
}

export function listRuntimeTasks(limit = 100): RuntimeTask[] {
  return tasks.slice(0, Math.max(1, Math.min(limit, 500)));
}

export function clearRuntimeTasks(): number {
  const count = tasks.length;
  tasks.splice(0, tasks.length);
  return count;
}

export function summarizeRuntimeQueue() {
  const counts: Record<RuntimeExecutionState, number> = {
    queued: 0,
    running: 0,
    blocked: 0,
    retrying: 0,
    failed: 0,
    completed: 0,
  };
  for (const task of tasks) {
    counts[task.status] += 1;
  }
  return {
    total: tasks.length,
    counts,
  };
}
