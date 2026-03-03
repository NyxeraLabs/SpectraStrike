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

const DEFAULT_NEXUS_URL = "https://127.0.0.1:18443";
const DEFAULT_VECTORVUE_URL = "https://127.0.0.1";

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

function browserFallback(fallback: string, port: string | null): string {
  if (typeof window === "undefined") return fallback;
  const host = window.location.hostname;
  if (!host) return fallback;
  const suffix = port ? `:${port}` : "";
  return `https://${host}${suffix}`;
}

function enforceHttps(name: string, value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return trimmed;
  if (trimmed.startsWith("https://")) return trimmed;
  if (trimmed.startsWith("http://")) {
    const upgraded = `https://${trimmed.slice("http://".length)}`;
    console.warn(`[cross-app-links] Insecure URL in ${name}. Upgrading to ${upgraded}`);
    return upgraded;
  }
  const upgraded = `https://${trimmed.replace(/^\/+/, "")}`;
  console.warn(`[cross-app-links] URL in ${name} missing scheme. Upgrading to ${upgraded}`);
  return upgraded;
}

export function getNexusUrl(): string {
  const configured =
    resolveEnv("VITE_NEXUS_URL") ||
    resolveEnv("NEXT_PUBLIC_NEXUS_URL") ||
    resolveEnv("UI_NEXUS_BASE_URL");
  if (configured) return enforceHttps("VITE_NEXUS_URL", configured);
  const fallback = browserFallback(DEFAULT_NEXUS_URL, "18443");
  warnMissing("VITE_NEXUS_URL", fallback);
  return fallback;
}

export function getVectorVueUrl(): string {
  const configured =
    resolveEnv("VITE_VECTORVUE_URL") ||
    resolveEnv("NEXT_PUBLIC_VECTORVUE_URL") ||
    resolveEnv("UI_VECTORVUE_BASE_URL");
  if (configured) return enforceHttps("VITE_VECTORVUE_URL", configured);
  const fallback = browserFallback(DEFAULT_VECTORVUE_URL, null);
  warnMissing("VITE_VECTORVUE_URL", fallback);
  return fallback;
}
