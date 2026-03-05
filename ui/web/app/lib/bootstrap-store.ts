/*
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
*/

export type BootstrapState = {
  tenants: string[];
  keys: string[];
  wrapperConfig: Record<string, { enabled: boolean; connectivity: "pending" | "ok" | "failed" }>;
  federationConfig: {
    endpoint: string;
    keyExchangeComplete: boolean;
    signatureTestPassed: boolean;
  } | null;
  platformOnboarded: boolean;
};

const state: BootstrapState = {
  tenants: [],
  keys: [],
  wrapperConfig: {},
  federationConfig: null,
  platformOnboarded: false,
};

export function getBootstrapState(): BootstrapState {
  return {
    tenants: [...state.tenants],
    keys: [...state.keys],
    wrapperConfig: { ...state.wrapperConfig },
    federationConfig: state.federationConfig ? { ...state.federationConfig } : null,
    platformOnboarded: state.platformOnboarded,
  };
}

export function getBootstrapZeroStatus(userCount: number) {
  return {
    users: userCount,
    tenants: state.tenants.length,
    keys: state.keys.length,
    wrapper_configured: Object.keys(state.wrapperConfig).length,
    federation_configured: state.federationConfig ? 1 : 0,
    is_db_zero:
      userCount === 0 &&
      state.tenants.length === 0 &&
      state.keys.length === 0 &&
      Object.keys(state.wrapperConfig).length === 0 &&
      state.federationConfig === null,
    platform_onboarded: state.platformOnboarded,
  };
}

export function applyBootstrapSetup(payload: {
  workspaceName: string;
  wrappers: string[];
  federationEndpoint: string;
}) {
  const workspace = payload.workspaceName.trim() || "default-workspace";
  state.tenants = [workspace];
  state.keys = ["spectrastrike-ed25519-public"];
  state.wrapperConfig = Object.fromEntries(
    payload.wrappers.map((wrapper) => [wrapper, { enabled: true, connectivity: "ok" as const }]),
  );
  state.federationConfig = {
    endpoint: payload.federationEndpoint,
    keyExchangeComplete: true,
    signatureTestPassed: true,
  };
  state.platformOnboarded = true;
}

export function resetBootstrapState() {
  const snapshot = getBootstrapState();
  state.tenants = [];
  state.keys = [];
  state.wrapperConfig = {};
  state.federationConfig = null;
  state.platformOnboarded = false;
  return snapshot;
}
