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
export const VECTORVUE_ONBOARDED_KEY = "vectorvue_onboarded";
export const NYXERA_DEMO_SESSION_KEY = "nyxera_demo_session";

export type SpectraDemoStep =
  | "welcome"
  | "palette_intro"
  | "drag_first_node"
  | "connect_nodes"
  | "configure_wrapper"
  | "add_to_queue"
  | "reorder_queue"
  | "run_execution"
  | "inspect_logs"
  | "inspect_telemetry"
  | "inspect_signature"
  | "federation_success"
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
  | "welcome"
  | "execution_list_intro"
  | "open_execution"
  | "signature_validation"
  | "attestation_review"
  | "policy_status"
  | "export_report"
  | "complete";

export type SpectraDemoAction =
  | "welcome_ack"
  | "palette_seen"
  | "node_dragged"
  | "nodes_connected"
  | "wrapper_configured"
  | "queued"
  | "queue_reordered"
  | "execution_started"
  | "logs_opened"
  | "telemetry_opened"
  | "signature_opened"
  | "federation_checked";

export const SPECTRA_DEMO_STEPS: SpectraDemoStep[] = [
  "welcome",
  "palette_intro",
  "drag_first_node",
  "connect_nodes",
  "configure_wrapper",
  "add_to_queue",
  "reorder_queue",
  "run_execution",
  "inspect_logs",
  "inspect_telemetry",
  "inspect_signature",
  "federation_success",
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
  "welcome",
  "execution_list_intro",
  "open_execution",
  "signature_validation",
  "attestation_review",
  "policy_status",
  "export_report",
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

export function canAdvanceSpectraStep(step: SpectraDemoStep, action: SpectraDemoAction): boolean {
  const guard: Record<SpectraDemoStep, SpectraDemoAction | null> = {
    welcome: "welcome_ack",
    palette_intro: "palette_seen",
    drag_first_node: "node_dragged",
    connect_nodes: "nodes_connected",
    configure_wrapper: "wrapper_configured",
    add_to_queue: "queued",
    reorder_queue: "queue_reordered",
    run_execution: "execution_started",
    inspect_logs: "logs_opened",
    inspect_telemetry: "telemetry_opened",
    inspect_signature: "signature_opened",
    federation_success: "federation_checked",
    complete: null,
  };
  return guard[step] === action;
}
