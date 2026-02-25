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
  const [lastDigest, setLastDigest] = useState("");
  const [authorized, setAuthorized] = useState<Array<{ tool_name: string; tool_sha256: string }>>([]);

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
      setLastDigest(body.tool_sha256 ?? "");
      setStatus(
        `Ingest accepted digest=${body.tool_sha256}. SBOM=${body.sbom_status} scan=${body.vuln_scan_status} signature=${body.signature_status}`
      );
    } catch (error) {
      setStatus(`Armory ingest failed: ${(error as Error).message}`);
    }
  }

  async function approveLast() {
    if (!lastDigest) {
      setStatus("No digest available. Ingest a tool first.");
      return;
    }
    setStatus(`Approving ${lastDigest} ...`);
    const response = await fetch("/ui/api/actions/armory/approve", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ tool_sha256: lastDigest }),
    });
    const body = await response.json();
    if (!response.ok) {
      setStatus(`Approval failed: ${body.error ?? `HTTP ${response.status}`}`);
      return;
    }
    setStatus(`Approved digest ${lastDigest} for runner execution.`);
    await refreshAuthorized();
  }

  async function refreshAuthorized() {
    const response = await fetch("/ui/api/actions/armory/authorized");
    const body = await response.json();
    if (!response.ok) {
      setStatus(`List failed: ${body.error ?? `HTTP ${response.status}`}`);
      return;
    }
    setAuthorized((body.items ?? []) as Array<{ tool_name: string; tool_sha256: string }>);
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
            <button
              type="button"
              onClick={approveLast}
              className="rounded-panel border border-borderSubtle bg-bgPrimary px-4 py-2 text-sm text-white"
            >
              Approve Last Digest
            </button>
            <button
              type="button"
              onClick={refreshAuthorized}
              className="rounded-panel border border-borderSubtle bg-bgPrimary px-4 py-2 text-sm text-white"
            >
              Refresh Authorized
            </button>
          </div>
        </form>
        <div className="mt-4 rounded-panel border border-borderSubtle bg-bgPrimary/50 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-400">Authorized Tool Digests</p>
          {authorized.length === 0 ? (
            <p className="mt-2 text-xs text-slate-400">No approved digests yet.</p>
          ) : (
            <ul className="mt-2 space-y-1 text-xs text-telemetryGlow">
              {authorized.map((item) => (
                <li key={item.tool_sha256}>
                  {item.tool_name} {"->"} {item.tool_sha256}
                </li>
              ))}
            </ul>
          )}
        </div>
        <p className="mt-4 text-xs text-telemetryGlow">{status}</p>
      </section>
    </main>
  );
}
