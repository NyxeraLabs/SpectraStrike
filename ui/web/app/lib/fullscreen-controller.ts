/*
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
*/

"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

function applyFullscreenClasses(active: boolean): void {
  if (typeof document === "undefined") return;
  document.body.classList.toggle("spectra-fullscreen-active", active);
  document.documentElement.classList.toggle("spectra-fullscreen-active", active);
  document.body.style.overflow = active ? "hidden" : "";
}

export function useFullscreenController() {
  const [fallbackActive, setFallbackActive] = useState(false);
  const [nativeActive, setNativeActive] = useState(false);

  useEffect(() => {
    if (typeof document === "undefined") return;
    const onFullscreenChange = () => {
      const active = document.fullscreenElement !== null;
      setNativeActive(active);
      if (!active) {
        setFallbackActive(false);
      }
      applyFullscreenClasses(active || fallbackActive);
    };
    document.addEventListener("fullscreenchange", onFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", onFullscreenChange);
  }, [fallbackActive]);

  useEffect(() => {
    applyFullscreenClasses(nativeActive || fallbackActive);
    return () => applyFullscreenClasses(false);
  }, [fallbackActive, nativeActive]);

  useEffect(() => {
    if (!fallbackActive || typeof window === "undefined") return;
    const onKeydown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setFallbackActive(false);
      }
    };
    window.addEventListener("keydown", onKeydown);
    return () => window.removeEventListener("keydown", onKeydown);
  }, [fallbackActive]);

  const isFullscreen = nativeActive || fallbackActive;

  const enter = useCallback(async () => {
    if (typeof document === "undefined") return;
    if (document.fullscreenElement) return;
    try {
      await document.documentElement.requestFullscreen();
    } catch {
      setFallbackActive(true);
    }
  }, []);

  const exit = useCallback(async () => {
    if (typeof document === "undefined") return;
    if (document.fullscreenElement) {
      await document.exitFullscreen().catch(() => undefined);
      return;
    }
    setFallbackActive(false);
  }, []);

  const toggle = useCallback(async () => {
    if (isFullscreen) {
      await exit();
      return;
    }
    await enter();
  }, [enter, exit, isFullscreen]);

  return useMemo(
    () => ({
      isFullscreen,
      enter,
      exit,
      toggle,
    }),
    [enter, exit, isFullscreen, toggle],
  );
}
