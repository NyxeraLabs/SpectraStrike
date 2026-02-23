import Link from "next/link";

import { TopNav } from "../components/top-nav";

const kpis = [
  { label: "Active Tasks", value: "7", tone: "text-info" },
  { label: "Open Findings", value: "12", tone: "text-warning" },
  { label: "Critical Findings", value: "2", tone: "text-critical" },
  { label: "Telemetry Events (24h)", value: "14,382", tone: "text-telemetryGlow" },
];

const quickActions = [
  "Queue Nmap scan",
  "Trigger Metasploit manual sync",
  "Review failed broker publishes",
  "Open audit chain validator",
];

export default function DashboardPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <article key={kpi.label} className="spectra-panel p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">{kpi.label}</p>
            <p className={`mt-2 text-2xl font-bold ${kpi.tone}`}>{kpi.value}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_1fr]">
        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Live Activity</h2>
          <div className="mt-4 space-y-3 text-sm text-slate-300">
            <p className="spectra-mono text-telemetryGlow">[telemetry] nmap_scan_completed target=10.0.9.0/24</p>
            <p className="spectra-mono text-success">[task] exploit_dispatch status=queued module=auxiliary/scanner/smb</p>
            <p className="spectra-mono text-warning">[broker] retry_attempt queue=spectrastrike.telemetry attempt=2</p>
            <p className="spectra-mono text-critical">[alert] policy_violation source=operator-session</p>
          </div>
          <div className="mt-4">
            <Link href="/dashboard/telemetry" className="spectra-button-primary inline-flex px-4 py-2 text-sm font-semibold">
              Open Full Telemetry Feed
            </Link>
          </div>
        </article>

        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-[0.2em] text-accentGlow">Quick Actions</h2>
          <div className="mt-4 grid gap-2">
            {quickActions.map((action) => (
              <button
                key={action}
                type="button"
                className="spectra-button-secondary flex items-center justify-between px-3 py-2 text-left text-sm"
              >
                <span>{action}</span>
                <span className="text-xs text-slate-400">run</span>
              </button>
            ))}
          </div>
          <div className="mt-4">
            <Link href="/dashboard/findings" className="spectra-button-primary inline-flex px-4 py-2 text-sm font-semibold">
              Open Findings Navigator
            </Link>
          </div>
        </article>
      </section>

      <section className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-slate-300">Operator Session</h2>
        <div className="mt-3 grid gap-2 text-sm text-slate-300 md:grid-cols-3">
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
        </div>
      </section>
    </main>
  );
}
