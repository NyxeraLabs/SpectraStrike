"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

type TelemetrySource = "nmap" | "metasploit" | "manual";
type TelemetryStatus = "success" | "info" | "warning" | "critical";

type TelemetryItem = {
  id?: string;
  event_id?: string;
  source: TelemetrySource;
  status: TelemetryStatus;
  eventType?: string;
  event_type?: string;
  actor: string;
  target: string;
  timestamp: string;
  details?: string;
};

const sourceBadgeClass: Record<TelemetrySource, string> = {
  nmap: "text-telemetryGlow border-telemetryDeep/70",
  metasploit: "text-accentGlow border-accentPrimary/50",
  manual: "text-info border-info/50",
};

const statusClass: Record<TelemetryStatus, string> = {
  success: "text-success",
  info: "text-info",
  warning: "text-warning",
  critical: "text-critical",
};

const fallbackItems: TelemetryItem[] = [
  {
    id: "evt-001",
    source: "nmap",
    status: "success",
    eventType: "nmap_scan_completed",
    actor: "scanner-daemon",
    target: "10.0.9.0/24",
    timestamp: "2026-02-23T18:20:31Z",
    details: "hosts=24 open_ports=43 elapsed_ms=1423",
  },
  {
    id: "evt-002",
    source: "metasploit",
    status: "info",
    eventType: "metasploit_session_ingested",
    actor: "msf-rpc-wrapper",
    target: "workspace/redteam-a",
    timestamp: "2026-02-23T18:19:02Z",
    details: "sessions=4 checkpoints=advanced",
  },
  {
    id: "evt-003",
    source: "manual",
    status: "warning",
    eventType: "manual_sync_partial",
    actor: "operator-jmicoli",
    target: "metasploit.remote.operator",
    timestamp: "2026-02-23T18:16:40Z",
    details: "event_page_timeout=true retry_pending=true",
  },
];

export function TelemetryFeedView() {
  const [source, setSource] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [cursor, setCursor] = useState<string>("");
  const [items, setItems] = useState<TelemetryItem[]>(fallbackItems);
  const [message, setMessage] = useState<string>("Using local fallback dataset.");

  const messageTone = useMemo(() => {
    if (message.toLowerCase().includes("loaded")) {
      return "text-success";
    }
    if (message.toLowerCase().includes("failed")) {
      return "text-critical";
    }
    return "text-slate-400";
  }, [message]);

  async function applyFilters() {
    const params = new URLSearchParams();
    if (source !== "all") {
      params.set("source", source);
    }
    if (status !== "all") {
      params.set("status", status);
    }
    if (cursor.trim()) {
      params.set("cursor", cursor.trim());
    }

    try {
      const response = await fetch(`/ui/api/telemetry/events?${params.toString()}`, {
        method: "GET",
        cache: "no-store",
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const body = await response.json();
      const nextItems = Array.isArray(body.items) ? body.items : [];
      setItems(nextItems);
      setMessage(`Loaded ${nextItems.length} telemetry events.`);
    } catch (error) {
      setItems(fallbackItems);
      setMessage(`Load failed: ${(error as Error).message}; fallback applied.`);
    }
  }

  function resetFilters() {
    setSource("all");
    setStatus("all");
    setCursor("");
    setItems(fallbackItems);
    setMessage("Filters reset; fallback dataset restored.");
  }

  return (
    <section className="flex flex-col gap-4">
      <article className="spectra-panel p-5">
        <h1 className="text-2xl font-bold text-white [font-family:var(--font-display)]">
          Telemetry Feed
        </h1>
        <p className="mt-2 text-sm text-slate-300">
          Unified Nmap, Metasploit, and manual ingestion telemetry stream.
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <label className="text-xs uppercase tracking-wide text-slate-400">
            Source
            <select
              value={source}
              onChange={(event) => setSource(event.target.value)}
              className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white"
            >
              <option value="all">All</option>
              <option value="nmap">Nmap</option>
              <option value="metasploit">Metasploit</option>
              <option value="manual">Manual</option>
            </select>
          </label>
          <label className="text-xs uppercase tracking-wide text-slate-400">
            Status
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white"
            >
              <option value="all">All</option>
              <option value="success">Success</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
          </label>
          <label className="text-xs uppercase tracking-wide text-slate-400">
            Cursor
            <input
              value={cursor}
              onChange={(event) => setCursor(event.target.value)}
              type="text"
              placeholder="evt-000"
              className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white"
            />
          </label>
          <div className="flex items-end gap-2">
            <button
              type="button"
              onClick={applyFilters}
              className="spectra-button-primary w-full px-4 py-2 text-sm font-semibold sm:w-auto"
            >
              Apply
            </button>
            <button
              type="button"
              onClick={resetFilters}
              className="spectra-button-secondary w-full px-4 py-2 text-sm font-semibold sm:w-auto"
            >
              Reset
            </button>
          </div>
        </div>
        <p className={`mt-3 text-xs ${messageTone}`}>{message}</p>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Live Stream</h2>
        <div className="mt-4 space-y-3">
          {items.map((item, index) => {
            const sourceKey = item.source;
            const statusKey = item.status;
            const key = item.event_id ?? item.id ?? `fallback-${index}`;
            const eventType = item.event_type ?? item.eventType ?? "unknown_event";

            return (
              <div key={key} className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`rounded-panel border px-2 py-1 text-xs uppercase tracking-wide ${sourceBadgeClass[sourceKey]}`}>
                    {sourceKey}
                  </span>
                  <span className={`text-xs font-semibold uppercase tracking-wide ${statusClass[statusKey]}`}>
                    {statusKey}
                  </span>
                  <span className="spectra-mono ml-auto text-xs text-slate-400">{item.timestamp}</span>
                </div>
                <p className="mt-2 spectra-mono break-all text-sm text-white">{eventType}</p>
                <p className="mt-1 break-all text-sm text-slate-300">
                  actor={item.actor} target={item.target}
                </p>
                {item.details ? (
                  <p className="mt-1 spectra-mono break-all text-xs text-slate-400">{item.details}</p>
                ) : null}
              </div>
            );
          })}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link href="/dashboard/findings" className="spectra-button-secondary px-4 py-2 text-sm font-semibold">
            Findings
          </Link>
          <Link href="/dashboard/findings/FND-2026-001/evidence" className="spectra-button-primary px-4 py-2 text-sm font-semibold">
            Jump to Evidence
          </Link>
        </div>
      </article>
    </section>
  );
}
