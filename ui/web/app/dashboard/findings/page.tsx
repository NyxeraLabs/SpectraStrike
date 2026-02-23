import Link from "next/link";

import { TopNav } from "../../components/top-nav";

export default function DashboardFindingsPlaceholderPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />
      <section className="spectra-panel p-6">
        <h1 className="text-2xl font-bold text-white [font-family:var(--font-display)]">
          Findings View
        </h1>
        <p className="mt-2 text-sm text-slate-300">
          Findings and evidence navigation screens are scheduled in Sprint 9.6 Step 5.
        </p>
        <div className="mt-4">
          <Link href="/dashboard" className="spectra-button-secondary inline-flex px-4 py-2 text-sm font-semibold">
            Back to Dashboard
          </Link>
        </div>
      </section>
    </main>
  );
}
