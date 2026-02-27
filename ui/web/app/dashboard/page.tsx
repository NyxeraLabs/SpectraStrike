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

import Link from "next/link";

import { QuickActions } from "../components/quick-actions";
import { TopNav } from "../components/top-nav";

const kpis = [
  { label: "Active Runners", value: "18", tone: "text-info" },
  { label: "MicroVM Sessions", value: "41", tone: "text-warning" },
  { label: "Queue Backlog", value: "12", tone: "text-critical" },
  { label: "Telemetry Events (24h)", value: "14,382", tone: "text-telemetryGlow" },
];

const defensiveMetrics = [
  { label: "Detection Rate", value: "67.1%", tone: "text-telemetryGlow" },
  { label: "Prevention Rate", value: "42.1%", tone: "text-warning" },
  { label: "Feedback Coverage", value: "58.3%", tone: "text-info" },
  { label: "Applied Adjustments", value: "37", tone: "text-success" },
];

export default function DashboardPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-6 sm:py-8">
      <TopNav />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <article key={kpi.label} className="spectra-panel p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">{kpi.label}</p>
            <p className={`mt-2 text-2xl font-bold ${kpi.tone}`}>{kpi.value}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_1fr]">
        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Execution Fabric Feed</h2>
          <div className="mt-4 space-y-3 text-sm text-slate-300">
            <p className="spectra-mono break-all text-telemetryGlow">
              [telemetry] nmap_scan_completed target=10.0.9.0/24
            </p>
            <p className="spectra-mono break-all text-success">
              [runner] microvm_boot status=success runtime=firecracker-sim
            </p>
            <p className="spectra-mono break-all text-warning">
              [queue] backlog depth=12 queue=telemetry.events
            </p>
            <p className="spectra-mono break-all text-critical">
              [trust] signer_health status=degraded key=spectrastrike-orchestrator-signing
            </p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Link
              href="/dashboard/telemetry"
              className="spectra-button-primary inline-flex px-4 py-2 text-sm font-semibold"
            >
              Open Full Telemetry Feed
            </Link>
          </div>
        </article>

        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Control Actions</h2>
          <QuickActions />
          <div className="mt-4 flex flex-wrap gap-2">
            <Link href="/dashboard/armory" className="spectra-button-secondary inline-flex px-4 py-2 text-sm font-semibold">
              Open Armory
            </Link>
            <Link href="/dashboard/fleet" className="spectra-button-secondary inline-flex px-4 py-2 text-sm font-semibold">
              Open Fleet
            </Link>
            <Link href="/dashboard/policy-trust" className="spectra-button-primary inline-flex px-4 py-2 text-sm font-semibold">
              Open Policy & Trust
            </Link>
          </div>
        </article>
      </section>

      <section className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-slate-300">Operator Session</h2>
        <div className="mt-3 grid gap-2 text-sm text-slate-300 sm:grid-cols-2 lg:grid-cols-4">
          <p>
            Role: <span className="spectra-mono text-white">red-team-operator</span>
          </p>
          <p>
            Auth Method: <span className="spectra-mono text-white">password+mfa</span>
          </p>
          <p>
            API Contract: <span className="spectra-mono text-white">GET /api/v1/dashboard/summary</span>
          </p>
          <p>
            Telemetry API: <span className="spectra-mono text-white">GET /api/v1/telemetry/events</span>
          </p>
          <p>
            Fleet API: <span className="spectra-mono text-white">GET /api/fleet/status</span>
          </p>
          <p>
            Armory API: <span className="spectra-mono text-white">POST /api/actions/armory/ingest</span>
          </p>
        </div>
      </section>

      <section className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-info">Defensive Effectiveness</h2>
        <p className="mt-2 text-sm text-slate-300">
          Cognitive loop metrics from <span className="spectra-mono text-white">GET /api/defensive/effectiveness</span>
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {defensiveMetrics.map((metric) => (
            <article key={metric.label} className="rounded-lg border border-white/10 bg-slate-950/70 p-3">
              <p className="text-xs uppercase tracking-wide text-slate-400">{metric.label}</p>
              <p className={`mt-2 text-xl font-bold ${metric.tone}`}>{metric.value}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
