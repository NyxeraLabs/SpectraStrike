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

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LegalAcceptancePage() {
  const router = useRouter();
  const [message, setMessage] = useState<string>("Acceptance required for platform access.");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submitAcceptance() {
    setIsSubmitting(true);
    setMessage("Recording legal acceptance...");
    try {
      const response = await fetch("/ui/api/v1/auth/legal/accept", {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify({
          accepted_by: "web-operator",
          accepted_documents: {
            eula: "2026.1",
            aup: "2026.1",
            privacy: "2026.1",
          },
        }),
      });
      const body = (await response.json()) as { error?: string; status?: string };
      if (!response.ok) {
        setMessage(`Unable to record acceptance: ${body.error ?? "unknown_error"}`);
        return;
      }

      setMessage("Acceptance recorded. You can now sign in.");
      router.push("/login");
      router.refresh();
    } catch {
      setMessage("Unable to reach legal acceptance endpoint.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-4 px-6 py-10">
      <section className="spectra-panel p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-telemetry">Governance</p>
        <h1 className="mt-2 text-3xl font-bold text-white [font-family:var(--font-display)]">
          Legal Acceptance Required
        </h1>
        <p className="mt-3 text-sm text-slate-300">
          Before authentication can continue, this installation requires active legal acceptance for
          current EULA, AUP, and Privacy versions.
        </p>
        <p className="mt-3 spectra-mono text-xs text-slate-400">
          versions: eula=2026.1 aup=2026.1 privacy=2026.1
        </p>

        <button
          type="button"
          onClick={submitAcceptance}
          disabled={isSubmitting}
          className="spectra-button-primary mt-5 px-4 py-2 text-sm font-semibold disabled:opacity-60"
        >
          {isSubmitting ? "Applying..." : "Accept Current Legal Terms"}
        </button>
        <p className="mt-3 text-xs text-slate-400">{message}</p>
      </section>
    </main>
  );
}
