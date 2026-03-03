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

import { cookies } from "next/headers";

import { NexusWorkbench } from "../../components/nexus-workbench";
import { TopNav } from "../../components/top-nav";
import { type NexusRole } from "../../lib/nexus-context";

const fallbackVectorVueBaseUrl = process.env.UI_VECTORVUE_BASE_URL ?? "http://localhost:3001";

function resolveRole(value: string | undefined): NexusRole {
  if (value === "admin" || value === "analyst" || value === "auditor") return value;
  return "operator";
}

export default async function NexusPage() {
  const cookieStore = await cookies();
  const tenantName = cookieStore.get("spectrastrike_tenant")?.value ?? "SpectraStrike Tenant";
  const tenantId = cookieStore.get("spectrastrike_tenant_id")?.value ?? "tenant-spectrastrike";
  const role = resolveRole(cookieStore.get("spectrastrike_role")?.value);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-6 sm:py-8">
      <TopNav />
      <section className="spectra-panel p-5">
        <h1 className="text-lg font-semibold text-white">Nexus Mode</h1>
        <p className="mt-2 text-sm text-slate-300">
          Unified navigation and validation context across SpectraStrike execution and VectorVue detection assurance.
        </p>
      </section>
      <NexusWorkbench tenantName={tenantName} tenantId={tenantId} role={role} vectorVueBaseUrl={fallbackVectorVueBaseUrl} />
    </main>
  );
}
