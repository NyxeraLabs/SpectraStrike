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
import { notFound } from "next/navigation";

import { findings } from "../../../components/findings-data";
import { TopNav } from "../../../components/top-nav";

export default async function FindingDetailPage({
  params: paramsPromise,
}: {
  params: Promise<{ findingId: string }>;
}) {
  const params = await paramsPromise;
  const finding = findings.find((item) => item.finding_id === params.findingId);
  if (!finding) {
    notFound();
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />
      <section className="spectra-panel p-6">
        <p className="spectra-mono text-xs text-slate-400">{finding.finding_id}</p>
        <h1 className="mt-2 text-2xl font-bold text-white [font-family:var(--font-display)]">
          {finding.title}
        </h1>
        <p className="mt-3 text-sm text-slate-300">{finding.summary}</p>

        <dl className="mt-5 grid gap-3 text-sm text-slate-300 md:grid-cols-2">
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-400">Severity</dt>
            <dd className="mt-1 text-white">{finding.severity}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-400">Status</dt>
            <dd className="mt-1 text-white">{finding.status}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-400">Source</dt>
            <dd className="mt-1 text-white">{finding.source}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-400">Target</dt>
            <dd className="mt-1 spectra-mono text-white">{finding.target}</dd>
          </div>
        </dl>

        <div className="mt-5 flex gap-2">
          <Link href="/dashboard/findings" className="spectra-button-secondary px-4 py-2 text-sm font-semibold">
            Back to Findings
          </Link>
          <Link
            href={`/dashboard/findings/${finding.finding_id}/evidence`}
            className="spectra-button-primary px-4 py-2 text-sm font-semibold"
          >
            Open Evidence
          </Link>
        </div>
      </section>
    </main>
  );
}
