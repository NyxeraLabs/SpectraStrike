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

import { legalDocuments } from "../../lib/legal-document-content";

type AcceptanceDocumentId = "eula" | "aup" | "privacy";

function isAcceptanceDocumentId(value: string): value is AcceptanceDocumentId {
  return value === "eula" || value === "aup" || value === "privacy";
}

type ApiErrorBody = {
  error?: string;
  status?: string;
};

async function parseApiErrorBody(response: Response): Promise<ApiErrorBody> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.toLowerCase().includes("application/json")) {
    return {};
  }
  try {
    return (await response.json()) as ApiErrorBody;
  } catch {
    return {};
  }
}

export default function LegalAcceptancePage() {
  const router = useRouter();
  const [message, setMessage] = useState<string>(
    "Acceptance required for platform access."
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [accepted, setAccepted] = useState<Record<AcceptanceDocumentId, boolean>>({
    eula: false,
    aup: false,
    privacy: false,
  });
  const [viewed, setViewed] = useState<Record<AcceptanceDocumentId, boolean>>({
    eula: false,
    aup: false,
    privacy: false,
  });

  const requiredDocs = legalDocuments
    .filter((document) => document.requiredForLegalAcceptance)
    .filter((document): document is (typeof legalDocuments)[number] & { id: AcceptanceDocumentId } =>
      isAcceptanceDocumentId(document.id)
    );
  const readyToSubmit = accepted.eula && accepted.aup && accepted.privacy;

  function markViewedIfScrolledToBottom(
    documentId: AcceptanceDocumentId,
    element: HTMLDivElement
  ) {
    const nearBottom = element.scrollTop + element.clientHeight >= element.scrollHeight - 4;
    if (!nearBottom || viewed[documentId]) {
      return;
    }
    setViewed((current) => ({
      ...current,
      [documentId]: true,
    }));
  }

  async function submitAcceptance() {
    if (!readyToSubmit) {
      setMessage("You must check all required legal documents before continuing.");
      return;
    }
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
            eula: requiredDocs.find((doc) => doc.id === "eula")?.version ?? "2026.1",
            aup: requiredDocs.find((doc) => doc.id === "aup")?.version ?? "2026.1",
            privacy:
              requiredDocs.find((doc) => doc.id === "privacy")?.version ?? "2026.1",
          },
        }),
      });
      const body = await parseApiErrorBody(response);
      if (!response.ok) {
        const reason =
          body.error ??
          `http_${response.status}${response.statusText ? `_${response.statusText}` : ""}`;
        setMessage(`Unable to record acceptance: ${reason}`);
        return;
      }

      setMessage("Acceptance recorded. You can now sign in.");
      router.push("/login");
      router.refresh();
    } catch (error) {
      const reason = error instanceof Error ? error.message : "network_error";
      setMessage(`Unable to reach legal acceptance endpoint: ${reason}`);
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
        <div className="mt-4 space-y-4">
          {requiredDocs.map((doc) => {
            const acceptanceId: AcceptanceDocumentId = doc.id;
            return (
              <article
                key={doc.id}
                className="rounded-panel border border-borderSubtle bg-bgPrimary/70 p-4"
              >
                <h2 className="text-sm font-semibold text-white">
                  {doc.title}
                  <span className="ml-2 spectra-mono text-xs text-slate-400">
                    v{doc.version}
                  </span>
                </h2>
                <div
                  className="mt-2 max-h-48 overflow-y-auto rounded-panel border border-borderSubtle bg-bgPrimary/80 p-3"
                  data-testid={`legal-accept-scroll-${doc.id}`}
                  onScroll={(event) => {
                    markViewedIfScrolledToBottom(acceptanceId, event.currentTarget);
                  }}
                >
                  <pre className="whitespace-pre-wrap text-xs leading-6 text-slate-300">
                    {doc.content}
                  </pre>
                </div>
                <p className="mt-2 text-xs text-slate-400">
                  {viewed[acceptanceId]
                    ? "Document reviewed."
                    : "Scroll to the end to enable acceptance."}
                </p>
                <label className="mt-3 flex cursor-pointer items-start gap-3 text-sm text-slate-200">
                  <input
                    type="checkbox"
                    checked={accepted[acceptanceId]}
                    onChange={() => {
                      if (!viewed[acceptanceId]) {
                        return;
                      }
                      setAccepted((current) => ({
                        ...current,
                        [acceptanceId]: !current[acceptanceId],
                      }));
                    }}
                    disabled={!viewed[acceptanceId]}
                    className="mt-1 h-4 w-4 rounded border-borderSubtle bg-bgPrimary text-accentPrimary"
                  />
                  <span>{doc.confirmLabel}</span>
                </label>
              </article>
            );
          })}
        </div>

        <button
          type="button"
          onClick={submitAcceptance}
          disabled={isSubmitting || !readyToSubmit}
          className="spectra-button-primary mt-5 px-4 py-2 text-sm font-semibold disabled:opacity-60"
        >
          {isSubmitting ? "Applying..." : "Accept Current Legal Terms"}
        </button>
        <p className="mt-3 text-xs text-slate-400">{message}</p>
      </section>
    </main>
  );
}
