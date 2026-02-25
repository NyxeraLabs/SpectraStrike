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

import { TopNav } from "../../components/top-nav";

type FleetStatus = {
  runners: { online: number; degraded: number; offline: number };
  microvms: { active: number; cold_pool: number };
  queues: { telemetry_events_depth: number; dead_letter_depth: number };
};

export default function DashboardFleetPage() {
  const fleet: FleetStatus = {
    runners: { online: 18, degraded: 2, offline: 1 },
    microvms: { active: 41, cold_pool: 8 },
    queues: { telemetry_events_depth: 12, dead_letter_depth: 1 },
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />
      <section className="spectra-panel p-6">
        <h1 className="text-2xl font-bold text-white [font-family:var(--font-display)]">Fleet Management</h1>
        <p className="mt-2 text-sm text-slate-300">
          Real-time health for edge runners, microVM execution pools, and broker queue pressure.
        </p>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <article className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">Runners</p>
            <p className="mt-2 text-sm text-success">online={fleet.runners.online}</p>
            <p className="text-sm text-warning">degraded={fleet.runners.degraded}</p>
            <p className="text-sm text-critical">offline={fleet.runners.offline}</p>
          </article>
          <article className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">MicroVMs</p>
            <p className="mt-2 text-sm text-telemetryGlow">active={fleet.microvms.active}</p>
            <p className="text-sm text-info">cold_pool={fleet.microvms.cold_pool}</p>
          </article>
          <article className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">Queues</p>
            <p className="mt-2 text-sm text-warning">telemetry.events={fleet.queues.telemetry_events_depth}</p>
            <p className="text-sm text-critical">dlq={fleet.queues.dead_letter_depth}</p>
          </article>
        </div>
      </section>
    </main>
  );
}
