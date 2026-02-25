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

export default function DashboardArmoryPage() {
  const [toolName, setToolName] = useState("nmap-secure");
  const [imageRef, setImageRef] = useState("registry.internal/security/nmap:1.0.0");
  const [status, setStatus] = useState("Ready for ingestion validation.");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Submitting Armory ingest...");
    try {
      const response = await fetch("/ui/api/actions/armory/ingest", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          tool_name: toolName,
          image_ref: imageRef,
          mode: "ingest",
        }),
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.error ?? `HTTP ${response.status}`);
      }
      setStatus(
        `Ingest accepted. SBOM=${body.sbom_status} scan=${body.vuln_scan_status} signature=${body.signature_status}`
      );
    } catch (error) {
      setStatus(`Armory ingest failed: ${(error as Error).message}`);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />
      <section className="spectra-panel p-6">
        <h1 className="text-2xl font-bold text-white [font-family:var(--font-display)]">Armory</h1>
        <p className="mt-2 text-sm text-slate-300">
          Register BYOT artifacts, run supply-chain controls, and prepare signed tool hashes for execution.
        </p>
        <form onSubmit={submit} className="mt-5 grid gap-4 rounded-panel border border-borderSubtle bg-bgPrimary/50 p-4 lg:grid-cols-2">
          <label className="text-sm text-slate-300">
            Tool Name
            <input
              className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white"
              value={toolName}
              onChange={(event) => setToolName(event.target.value)}
            />
          </label>
          <label className="text-sm text-slate-300">
            OCI Image / Artifact Ref
            <input
              className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white"
              value={imageRef}
              onChange={(event) => setImageRef(event.target.value)}
            />
          </label>
          <div className="lg:col-span-2 flex gap-2">
            <button type="submit" className="spectra-button-primary px-4 py-2 text-sm font-semibold">
              Ingest + Scan + Sign
            </button>
          </div>
        </form>
        <p className="mt-4 text-xs text-telemetryGlow">{status}</p>
      </section>
    </main>
  );
}
