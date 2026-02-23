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

import { findings } from "../../components/findings-data";
import { TopNav } from "../../components/top-nav";

const severityClass = {
  low: "text-info",
  medium: "text-warning",
  high: "text-accentGlow",
  critical: "text-critical",
};

const statusClass = {
  open: "text-warning",
  accepted: "text-info",
  resolved: "text-success",
};

export default function DashboardFindingsPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />

      <section className="spectra-panel p-6">
        <h1 className="text-2xl font-bold text-white [font-family:var(--font-display)]">Findings</h1>
        <p className="mt-2 text-sm text-slate-300">
          Navigate validated findings and pivot into evidence details.
        </p>

        <div className="mt-5 grid gap-3">
          {findings.map((finding) => (
            <article key={finding.finding_id} className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`text-xs font-semibold uppercase tracking-wide ${severityClass[finding.severity]}`}>
                  {finding.severity}
                </span>
                <span className={`text-xs uppercase tracking-wide ${statusClass[finding.status]}`}>
                  {finding.status}
                </span>
                <span className="spectra-mono ml-auto text-xs text-slate-400">{finding.finding_id}</span>
              </div>
              <h2 className="mt-2 text-lg font-semibold text-white">{finding.title}</h2>
              <p className="mt-1 text-sm text-slate-300">{finding.summary}</p>
              <p className="mt-2 text-xs text-slate-400">
                source={finding.source} target={finding.target} updated={finding.updated_at}
              </p>
              <div className="mt-3 flex gap-2">
                <Link
                  href={`/dashboard/findings/${finding.finding_id}`}
                  className="spectra-button-secondary px-3 py-2 text-xs font-semibold"
                >
                  Open Finding
                </Link>
                <Link
                  href={`/dashboard/findings/${finding.finding_id}/evidence`}
                  className="spectra-button-primary px-3 py-2 text-xs font-semibold"
                >
                  View Evidence
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
