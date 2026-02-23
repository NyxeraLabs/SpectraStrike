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

import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-12">
      <header className="spectra-panel bg-surfaceElevated/80 p-8">
        <Image
          src="/ui/assets/spectrastrike-logo.png"
          alt="SpectraStrike logo"
          width={520}
          height={347}
          className="rounded-lg border border-borderSubtle/80"
          priority
        />
        <p className="text-xs uppercase tracking-[0.2em] text-telemetry">Sprint 9.6</p>
        <h1 className="mt-3 text-4xl font-bold text-white [font-family:var(--font-display)]">
          SpectraStrike Web Console
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">
          Dockerized Next.js foundation is online. Authentication view and operator dashboard shell
          are now available for endpoint wiring in subsequent Sprint 9.6 steps.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/login" className="spectra-button-primary px-4 py-2 text-sm font-semibold">
            Open Login
          </Link>
          <Link href="/dashboard" className="spectra-button-secondary px-4 py-2 text-sm font-semibold">
            Open Dashboard
          </Link>
        </div>
      </header>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-wide text-telemetryGlow">Runtime</h2>
          <p className="mt-2 text-lg font-medium text-white">Containerized</p>
        </article>
        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-wide text-telemetryGlow">Route</h2>
          <p className="mt-2 text-lg font-medium text-white">/ui</p>
        </article>
        <article className="spectra-panel p-5">
          <h2 className="text-sm uppercase tracking-wide text-telemetryGlow">Status</h2>
          <p className="mt-2 text-lg font-medium text-success">Foundation Ready</p>
        </article>
      </section>

      <section className="mt-8 spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-wide text-accentGlow">Telemetry Preview</h2>
        <pre className="spectra-mono mt-3 overflow-x-auto text-xs text-slate-300">
          {`event_type=nmap_scan_completed status=success latency_ms=142
event_type=metasploit_session_ingested status=info count=4
event_type=broker_publish status=success exchange=spectrastrike.telemetry`}
        </pre>
      </section>
    </main>
  );
}
