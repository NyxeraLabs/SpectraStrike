/*
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
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

import { getNexusUrl, getVectorVueUrl } from "./cross-app-links";

export const SPECTRA_ONBOARDED_KEY = "spectrastrike_onboarded";

export type SpectraDemoStep =
  | "intro"
  | "canvas_intro"
  | "auto_build_playbook"
  | "link_nodes"
  | "queue_nodes"
  | "execute_demo"
  | "inspect_telemetry"
  | "open_nexus"
  | "complete";

export type NexusDemoStep =
  | "intro"
  | "execution_list"
  | "execution_detail"
  | "telemetry_overview"
  | "signature_validation"
  | "attestation_view"
  | "open_vectorvue"
  | "complete";

export type VectorVueDemoStep =
  | "intro"
  | "envelope_intake"
  | "signature_check"
  | "attestation_verification"
  | "measurement_hash"
  | "policy_validation"
  | "return_to_spectrastrike"
  | "complete";

export const SPECTRA_DEMO_STEPS: SpectraDemoStep[] = [
  "intro",
  "canvas_intro",
  "auto_build_playbook",
  "link_nodes",
  "queue_nodes",
  "execute_demo",
  "inspect_telemetry",
  "open_nexus",
  "complete",
];

export const NEXUS_DEMO_STEPS: NexusDemoStep[] = [
  "intro",
  "execution_list",
  "execution_detail",
  "telemetry_overview",
  "signature_validation",
  "attestation_view",
  "open_vectorvue",
  "complete",
];

export const VECTORVUE_DEMO_STEPS: VectorVueDemoStep[] = [
  "intro",
  "envelope_intake",
  "signature_check",
  "attestation_verification",
  "measurement_hash",
  "policy_validation",
  "return_to_spectrastrike",
  "complete",
];

export function shouldStartSpectraDemo(storage: Pick<Storage, "getItem">): boolean {
  return storage.getItem(SPECTRA_ONBOARDED_KEY) !== "true";
}

export function buildNexusDemoUrl(): string {
  const base = getNexusUrl().replace(/\/$/, "");
  return `${base}/?demo=true&source=spectrastrike`;
}

export function buildVectorVueDemoUrl(): string {
  const base = getVectorVueUrl().replace(/\/$/, "");
  return `${base}/portal/validation?demo=true&source=nexus`;
}

export function isDemoQuery(search: string): boolean {
  const query = search.startsWith("?") ? search.slice(1) : search;
  const params = new URLSearchParams(query);
  return params.get("demo") === "true";
}

export function nextDemoStep<T extends string>(steps: readonly T[], current: T): T {
  const idx = steps.indexOf(current);
  if (idx < 0 || idx + 1 >= steps.length) return steps[steps.length - 1];
  return steps[idx + 1];
}
