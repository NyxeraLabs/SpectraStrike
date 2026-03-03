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

export type UiTheme = "dark" | "light";
export type GlobalRole = "red_team" | "blue_team" | "exec" | "auditor";

export type WorkspaceState = {
  theme: UiTheme;
  powerMode: boolean;
  role: GlobalRole;
  lastPath: string;
};

const allowedRoles: GlobalRole[] = ["red_team", "blue_team", "exec", "auditor"];

export function nextTheme(theme: UiTheme): UiTheme {
  return theme === "dark" ? "light" : "dark";
}

export function roleLabel(role: GlobalRole): string {
  if (role === "red_team") return "Red Team";
  if (role === "blue_team") return "Blue Team";
  if (role === "exec") return "Exec";
  return "Auditor";
}

export function roleAllowsPowerMode(role: GlobalRole): boolean {
  return role === "red_team" || role === "blue_team" || role === "exec";
}

export function roleCanExport(role: GlobalRole): boolean {
  return role === "auditor" || role === "exec";
}

export function applyTheme(theme: UiTheme): void {
  if (typeof document === "undefined") return;
  document.documentElement.setAttribute("data-theme", theme);
}

export function parseWorkspaceState(raw: string | null): WorkspaceState {
  const fallback: WorkspaceState = {
    theme: "dark",
    powerMode: false,
    role: "red_team",
    lastPath: "/dashboard",
  };
  if (!raw) return fallback;
  try {
    const parsed = JSON.parse(raw) as Partial<WorkspaceState>;
    const role = parsed.role && allowedRoles.includes(parsed.role) ? parsed.role : fallback.role;
    const theme = parsed.theme === "light" ? "light" : "dark";
    const powerMode = parsed.powerMode === true;
    const lastPath = typeof parsed.lastPath === "string" && parsed.lastPath.startsWith("/") ? parsed.lastPath : fallback.lastPath;
    return { theme, powerMode, role, lastPath };
  } catch {
    return fallback;
  }
}

export function encodeWorkspaceState(state: WorkspaceState): string {
  return JSON.stringify(state);
}

export function keyboardShortcutTarget(key: string, altPressed: boolean): string | null {
  if (!altPressed) return null;
  if (key === "1") return "/dashboard";
  if (key === "2") return "/dashboard/workflow";
  if (key === "3") return "/dashboard/nexus";
  if (key === "4") return "/dashboard/telemetry";
  return null;
}

export function reduceRenderBudget<T>(items: T[], maxItems: number): T[] {
  const limit = Math.max(10, Math.min(1000, maxItems));
  return items.slice(0, limit);
}

export function accessibilityChecklist(): Array<{ id: string; status: "pass" | "warn" }> {
  return [
    { id: "keyboard-navigation", status: "pass" },
    { id: "focus-visible", status: "pass" },
    { id: "contrast-ratio", status: "pass" },
    { id: "aria-live-feedback", status: "pass" },
  ];
}
