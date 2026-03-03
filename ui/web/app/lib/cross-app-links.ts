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

const DEFAULT_NEXUS_URL = "http://localhost:3001";
const DEFAULT_VECTORVUE_URL = "http://localhost:3002";

function clean(value: string | undefined): string {
  return String(value ?? "").trim();
}

function resolveEnv(name: string): string {
  if (typeof process !== "undefined" && process.env) {
    return clean(process.env[name]);
  }
  return "";
}

function warnMissing(name: string, fallback: string): void {
  // Keep warning explicit so operators can spot misconfigured cross-plane routing quickly.
  console.warn(`[cross-app-links] Missing env ${name}. Falling back to ${fallback}`);
}

export function getNexusUrl(): string {
  const configured =
    resolveEnv("VITE_NEXUS_URL") ||
    resolveEnv("NEXT_PUBLIC_NEXUS_URL") ||
    resolveEnv("UI_NEXUS_BASE_URL");
  if (configured) return configured;
  warnMissing("VITE_NEXUS_URL", DEFAULT_NEXUS_URL);
  return DEFAULT_NEXUS_URL;
}

export function getVectorVueUrl(): string {
  const configured =
    resolveEnv("VITE_VECTORVUE_URL") ||
    resolveEnv("NEXT_PUBLIC_VECTORVUE_URL") ||
    resolveEnv("UI_VECTORVUE_BASE_URL");
  if (configured) return configured;
  warnMissing("VITE_VECTORVUE_URL", DEFAULT_VECTORVUE_URL);
  return DEFAULT_VECTORVUE_URL;
}
