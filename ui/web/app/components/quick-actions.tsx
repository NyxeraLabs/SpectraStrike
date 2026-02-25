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

"use client";

import { useMemo, useState } from "react";

type ActionResult = {
  status: "idle" | "pending" | "ok" | "error";
  message: string;
};

const defaultResult: ActionResult = {
  status: "idle",
  message: "",
};

export function QuickActions() {
  const [result, setResult] = useState<ActionResult>(defaultResult);

  const resultClass = useMemo(() => {
    if (result.status === "ok") {
      return "text-success";
    }
    if (result.status === "error") {
      return "text-critical";
    }
    if (result.status === "pending") {
      return "text-telemetryGlow";
    }
    return "text-slate-400";
  }, [result.status]);

  async function runTask(tool: string, target: string, parameters: Record<string, unknown> = {}) {
    setResult({ status: "pending", message: `Submitting ${tool} task...` });

    try {
      const response = await fetch("/ui/api/actions/tasks", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ tool, target, parameters }),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.error ?? `HTTP ${response.status}`);
      }

      const body = await response.json();
      setResult({ status: "ok", message: `Task queued (${body.task_id ?? "n/a"})` });
    } catch (error) {
      setResult({ status: "error", message: `Action failed: ${(error as Error).message}` });
    }
  }

  async function runRunnerKillAll() {
    setResult({ status: "pending", message: "Issuing break-glass runner shutdown..." });

    try {
      const response = await fetch("/ui/api/actions/runner/kill-all", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ reason: "ui_break_glass" }),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.error ?? `HTTP ${response.status}`);
      }

      const body = await response.json();
      setResult({
        status: "ok",
        message: `Runner shutdown complete (${body.destroyed_microvms ?? 0} microVMs)`,
      });
    } catch (error) {
      setResult({ status: "error", message: `Runner shutdown failed: ${(error as Error).message}` });
    }
  }

  return (
    <div className="mt-4 grid gap-2">
      <button
        type="button"
        onClick={() => runTask("nmap", "10.0.9.0/24")}
        className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
      >
        <span>Queue Nmap Scan</span>
        <span className="text-xs text-slate-400">run</span>
      </button>
      <button
        type="button"
        onClick={() => runTask("armory-ingest", "armory", { mode: "dry_run" })}
        className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
      >
        <span>Run Armory Ingest Validation</span>
        <span className="text-xs text-slate-400">run</span>
      </button>
      <button
        type="button"
        onClick={() => runTask("queue-health-check", "telemetry.events", { includeDepth: true })}
        className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
      >
        <span>Check Queue Health</span>
        <span className="text-xs text-slate-400">run</span>
      </button>
      <button
        type="button"
        onClick={runRunnerKillAll}
        className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
      >
        <span>Break-Glass: Kill Active Runners</span>
        <span className="text-xs text-slate-400">run</span>
      </button>

      <p className={`mt-2 text-xs ${resultClass}`}>{result.message || "No action executed yet."}</p>
    </div>
  );
}
