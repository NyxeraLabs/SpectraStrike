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

import { AsmWorkbench } from "../../components/asm-workbench";
import { TopNav } from "../../components/top-nav";

export default function AsmGraphPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-6 sm:py-8">
      <div className="spectra-fullscreen-hide">
        <TopNav />
      </div>
      <section className="spectra-panel p-5 spectra-fullscreen-hide">
        <h1 className="text-lg font-semibold text-white">ASM Graph Engine</h1>
        <p className="mt-2 text-sm text-slate-300">
          Attack-surface graph modeling for asset relationships, exposure pivots, cloud IAM links, and playbook conversion.
        </p>
      </section>
      <AsmWorkbench />
    </main>
  );
}
