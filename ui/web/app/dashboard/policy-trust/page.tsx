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

import { FormEvent, useState } from "react";

import { TopNav } from "../../components/top-nav";

const defaultRego = `package spectrastrike.execution

default allow = false

allow if {
  input.tenant_id == "tenant-a"
  startswith(input.target_urn, "urn:target:ip:")
}`;

export default function DashboardPolicyTrustPage() {
  const [rego, setRego] = useState(defaultRego);
  const [status, setStatus] = useState("Policy editor ready.");

  async function applyPolicy(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Applying policy bundle...");
    try {
      const response = await fetch("/ui/api/policy-trust/apply", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ rego_source: rego }),
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.error ?? `HTTP ${response.status}`);
      }
      setStatus(`Policy applied: bundle=${body.policy_bundle_version} lines=${body.lines_received}`);
    } catch (error) {
      setStatus(`Policy apply failed: ${(error as Error).message}`);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />
      <section className="spectra-panel p-6">
        <h1 className="text-2xl font-bold text-white [font-family:var(--font-display)]">Policy & Trust</h1>
        <p className="mt-2 text-sm text-slate-300">
          Manage OPA execution policy and monitor Vault signing trust-state for JWS issuance.
        </p>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <article className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">Vault Transit</p>
            <p className="mt-2 text-sm text-success">status=healthy</p>
            <p className="text-sm text-telemetryGlow">key=spectrastrike-orchestrator-signing</p>
            <p className="text-sm text-info">latest_version=3</p>
          </article>
          <article className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">OPA Bundle</p>
            <p className="mt-2 text-sm text-success">status=healthy</p>
            <p className="text-sm text-telemetryGlow">bundle=2026.02.25.1</p>
            <p className="text-sm text-info">last_reload=2026-02-25T17:40:00Z</p>
          </article>
        </div>
        <form onSubmit={applyPolicy} className="mt-5 rounded-panel border border-borderSubtle bg-bgPrimary/50 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-400">OPA Rego Editor</p>
          <textarea
            value={rego}
            onChange={(event) => setRego(event.target.value)}
            className="spectra-mono mt-3 min-h-[220px] w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-xs text-white"
          />
          <div className="mt-3">
            <button type="submit" className="spectra-button-primary px-4 py-2 text-sm font-semibold">
              Apply Policy Bundle
            </button>
          </div>
        </form>
        <p className="mt-4 text-xs text-telemetryGlow">{status}</p>
      </section>
    </main>
  );
}
