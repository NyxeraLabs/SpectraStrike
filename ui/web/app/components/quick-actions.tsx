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

  async function runTask(tool: string, target: string) {
    setResult({ status: "pending", message: `Submitting ${tool} task...` });

    try {
      const response = await fetch("/ui/api/actions/tasks", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ tool, target, parameters: {} }),
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

  async function runManualSync() {
    setResult({ status: "pending", message: "Triggering manual sync..." });

    try {
      const response = await fetch("/ui/api/actions/manual-sync", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ actor: "ui-operator" }),
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.error ?? `HTTP ${response.status}`);
      }

      const body = await response.json();
      setResult({
        status: "ok",
        message: `Manual sync complete (${body.observed_session_events ?? 0} events)`,
      });
    } catch (error) {
      setResult({ status: "error", message: `Sync failed: ${(error as Error).message}` });
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
        onClick={runManualSync}
        className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
      >
        <span>Trigger Metasploit Manual Sync</span>
        <span className="text-xs text-slate-400">run</span>
      </button>
      <button
        type="button"
        onClick={() => runTask("telemetry-retry", "spectrastrike.telemetry")}
        className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
      >
        <span>Retry Broker Delivery</span>
        <span className="text-xs text-slate-400">run</span>
      </button>
      <button
        type="button"
        onClick={() => runTask("audit-chain-check", "orchestrator")}
        className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
      >
        <span>Validate Audit Chain</span>
        <span className="text-xs text-slate-400">run</span>
      </button>

      <p className={`mt-2 text-xs ${resultClass}`}>{result.message || "No action executed yet."}</p>
    </div>
  );
}
