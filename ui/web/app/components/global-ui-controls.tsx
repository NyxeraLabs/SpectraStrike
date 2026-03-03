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

import React, { useEffect, useMemo, useState } from "react";

import {
  accessibilityChecklist,
  applyTheme,
  encodeWorkspaceState,
  keyboardShortcutTarget,
  nextTheme,
  parseWorkspaceState,
  reduceRenderBudget,
  roleAllowsPowerMode,
  roleCanExport,
  roleLabel,
  type GlobalRole,
  type UiTheme,
} from "../lib/global-ui";

type Notice = {
  id: string;
  tone: "info" | "success";
  text: string;
};

const storageKey = "spectra_workspace_state_v1";

export function GlobalUiControls() {
  const [theme, setTheme] = useState<UiTheme>("dark");
  const [role, setRole] = useState<GlobalRole>("red_team");
  const [powerMode, setPowerMode] = useState(false);
  const [lastPath, setLastPath] = useState("/dashboard");
  const [health, setHealth] = useState("nominal");
  const [notices, setNotices] = useState<Notice[]>([]);

  useEffect(() => {
    const restored = parseWorkspaceState(localStorage.getItem(storageKey));
    setTheme(restored.theme);
    setRole(restored.role);
    setPowerMode(restored.powerMode);
    setLastPath(restored.lastPath);
    applyTheme(restored.theme);
  }, []);

  useEffect(() => {
    const snapshot = encodeWorkspaceState({
      theme,
      role,
      powerMode,
      lastPath: window.location.pathname,
    });
    localStorage.setItem(storageKey, snapshot);
  }, [lastPath, powerMode, role, theme]);

  useEffect(() => {
    const timer = setInterval(() => {
      const now = Date.now();
      setHealth(now % 5 === 0 ? "degraded" : "nominal");
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = keyboardShortcutTarget(event.key, event.altKey);
      if (target) {
        event.preventDefault();
        setLastPath(target);
        window.location.assign(target);
        return;
      }
      if (event.key.toLowerCase() === "k" && event.ctrlKey) {
        event.preventDefault();
        if (roleAllowsPowerMode(role)) {
          setPowerMode((prev) => !prev);
          setNotices((prev) =>
            reduceRenderBudget(
              [{ id: `${Date.now()}`, tone: "info", text: `Power mode ${!powerMode ? "enabled" : "disabled"}` }, ...prev],
              4,
            ),
          );
        }
      }
    };

    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [powerMode, role]);

  const a11y = useMemo(() => accessibilityChecklist(), []);
  const currentPath = typeof window === "undefined" ? "" : window.location.pathname;
  const hasRecover = Boolean(currentPath) && lastPath !== currentPath;

  return (
    <div className="flex flex-wrap items-center gap-2" aria-live="polite">
      <button
        type="button"
        className="spectra-button-secondary px-2 py-1 text-xs font-semibold"
        onClick={() => {
          const next = nextTheme(theme);
          setTheme(next);
          applyTheme(next);
        }}
      >
        Theme: {theme}
      </button>

      <label className="text-xs text-slate-300">
        <span className="sr-only">Role selector</span>
        <select
          value={role}
          onChange={(event) => setRole(event.target.value as GlobalRole)}
          className="rounded border border-borderSubtle bg-slate-950/80 px-2 py-1 text-xs text-white"
        >
          <option value="red_team">Red Team</option>
          <option value="blue_team">Blue Team</option>
          <option value="exec">Exec</option>
          <option value="auditor">Auditor</option>
        </select>
      </label>

      <span className={`rounded border px-2 py-1 text-xs ${health === "nominal" ? "border-success text-success" : "border-warning text-warning"}`}>
        Health: {health}
      </span>

      <button
        type="button"
        className="spectra-button-secondary px-2 py-1 text-xs"
        onClick={() =>
          setNotices((prev) =>
            reduceRenderBudget(
              [{ id: `${Date.now()}`, tone: "success", text: `${roleLabel(role)} context refreshed` }, ...prev],
              4,
            ),
          )
        }
      >
        Notify
      </button>

      {hasRecover ? (
        <button
          type="button"
          className="spectra-button-primary px-2 py-1 text-xs"
          onClick={() => window.location.assign(lastPath)}
        >
          Recover Workspace
        </button>
      ) : null}

      <span className="text-xs text-slate-400">
        Power: {powerMode ? "on" : "off"} | Export: {roleCanExport(role) ? "enabled" : "restricted"}
      </span>

      {notices.length > 0 ? (
        <ul className="ml-2 flex max-w-[320px] flex-col gap-1 text-xs" data-testid="global-notifications">
          {notices.map((notice) => (
            <li
              key={notice.id}
              className={`rounded border px-2 py-1 ${notice.tone === "success" ? "border-success text-success" : "border-info text-info"}`}
            >
              {notice.text}
            </li>
          ))}
        </ul>
      ) : null}

      <span className="sr-only">A11y checks: {a11y.map((row) => `${row.id}:${row.status}`).join(",")}</span>
    </div>
  );
}
