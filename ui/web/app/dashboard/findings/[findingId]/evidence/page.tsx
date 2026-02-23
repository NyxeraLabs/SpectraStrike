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

import { evidenceByFindingId, findings } from "../../../../components/findings-data";
import { TopNav } from "../../../../components/top-nav";

export default async function FindingEvidencePage({
  params: paramsPromise,
}: {
  params: Promise<{ findingId: string }>;
}) {
  const params = await paramsPromise;
  const finding = findings.find((item) => item.finding_id === params.findingId);
  if (!finding) {
    notFound();
  }

  const evidenceItems = evidenceByFindingId[finding.finding_id] ?? [];

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />
      <section className="spectra-panel p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-telemetry">Evidence</p>
        <h1 className="mt-2 text-2xl font-bold text-white [font-family:var(--font-display)]">
          {finding.finding_id}
        </h1>
        <p className="mt-2 text-sm text-slate-300">{finding.title}</p>

        <div className="mt-5 grid gap-3">
          {evidenceItems.map((item) => (
            <article key={item.evidence_id} className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
              <p className="spectra-mono text-xs text-slate-400">{item.evidence_id}</p>
              <p className="mt-1 text-sm text-white">type={item.type}</p>
              <p className="mt-1 spectra-mono text-xs text-slate-300">{item.content_ref}</p>
              <p className="mt-1 text-xs text-slate-400">captured_at={item.captured_at}</p>
            </article>
          ))}
        </div>

        <div className="mt-5 flex gap-2">
          <Link
            href={`/dashboard/findings/${finding.finding_id}`}
            className="spectra-button-secondary px-4 py-2 text-sm font-semibold"
          >
            Back to Finding
          </Link>
          <Link href="/dashboard/findings" className="spectra-button-primary px-4 py-2 text-sm font-semibold">
            All Findings
          </Link>
        </div>
      </section>
    </main>
  );
}
