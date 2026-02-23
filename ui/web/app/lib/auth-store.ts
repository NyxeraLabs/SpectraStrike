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

import { randomBytes, scrypt as scryptCallback, timingSafeEqual } from "node:crypto";
import { promisify } from "node:util";

import { legalEnforcementService } from "./legal-enforcement";

const scrypt = promisify(scryptCallback);
const sessionTtlSeconds = 8 * 60 * 60;

type StoredUser = {
  id: string;
  username: string;
  usernameKey: string;
  fullName: string;
  email: string;
  roles: string[];
  passwordSaltHex: string;
  passwordHashHex: string;
  createdAt: string;
  acceptedPoliciesAt: string;
};

type StoredSession = {
  token: string;
  userId: string;
  expiresAtMs: number;
};

type RegisterUserInput = {
  username: string;
  fullName: string;
  email: string;
  password: string;
  acceptedPoliciesAt: string;
};

type PublicUser = {
  id: string;
  username: string;
  fullName: string;
  email: string;
  roles: string[];
  createdAt: string;
};

type AuthDataStore = {
  usersByKey: Map<string, StoredUser>;
  sessionsByToken: Map<string, StoredSession>;
  bootstrapPromise: Promise<void> | null;
  demoPromise: Promise<PublicUser> | null;
};

export type AuthValidationResult = {
  ok: boolean;
  error?: "unauthorized" | "LEGAL_ACCEPTANCE_REQUIRED";
  legal?: {
    environment: "self-hosted" | "enterprise" | "saas";
    reason?: string;
    requires_reacceptance: boolean;
  };
};

const globalStoreKey = "__spectrastrikeAuthStore__";
const store = (globalThis as Record<string, unknown>)[globalStoreKey] as AuthDataStore | undefined;

const authStore: AuthDataStore = store ?? {
  usersByKey: new Map<string, StoredUser>(),
  sessionsByToken: new Map<string, StoredSession>(),
  bootstrapPromise: null,
  demoPromise: null,
};

if (!store) {
  (globalThis as Record<string, unknown>)[globalStoreKey] = authStore;
}

function normalizeUsername(username: string): string {
  return username.trim().toLowerCase();
}

function toPublicUser(user: StoredUser): PublicUser {
  return {
    id: user.id,
    username: user.username,
    fullName: user.fullName,
    email: user.email,
    roles: user.roles,
    createdAt: user.createdAt,
  };
}

async function hashPassword(password: string, saltHex?: string): Promise<{ saltHex: string; hashHex: string }> {
  const salt = saltHex ? Buffer.from(saltHex, "hex") : randomBytes(16);
  const derived = (await scrypt(password, salt, 64)) as Buffer;
  return {
    saltHex: salt.toString("hex"),
    hashHex: derived.toString("hex"),
  };
}

async function createUser(input: RegisterUserInput): Promise<StoredUser> {
  const usernameKey = normalizeUsername(input.username);
  const { saltHex, hashHex } = await hashPassword(input.password);
  const user: StoredUser = {
    id: `usr-${randomBytes(8).toString("hex")}`,
    username: input.username,
    usernameKey,
    fullName: input.fullName,
    email: input.email,
    roles: ["operator"],
    passwordSaltHex: saltHex,
    passwordHashHex: hashHex,
    createdAt: new Date().toISOString(),
    acceptedPoliciesAt: input.acceptedPoliciesAt,
  };
  authStore.usersByKey.set(usernameKey, user);
  return user;
}

async function verifyPassword(password: string, saltHex: string, expectedHashHex: string): Promise<boolean> {
  const derived = await hashPassword(password, saltHex);
  const expected = Buffer.from(expectedHashHex, "hex");
  const received = Buffer.from(derived.hashHex, "hex");
  if (expected.length !== received.length) {
    return false;
  }
  return timingSafeEqual(expected, received);
}

export async function ensureBootstrapUser(): Promise<void> {
  if (authStore.bootstrapPromise) {
    await authStore.bootstrapPromise;
    return;
  }

  authStore.bootstrapPromise = (async () => {
    const defaultUsername = process.env.UI_AUTH_BOOTSTRAP_USERNAME ?? "operator";
    const userKey = normalizeUsername(defaultUsername);
    if (authStore.usersByKey.has(userKey)) {
      return;
    }

    const defaultPassword = process.env.UI_AUTH_BOOTSTRAP_PASSWORD ?? "Operator!ChangeMe123";
    const defaultFullName = process.env.UI_AUTH_BOOTSTRAP_FULL_NAME ?? "Default Operator";
    const defaultEmail = process.env.UI_AUTH_BOOTSTRAP_EMAIL ?? "operator@spectrastrike.local";
    const nowIso = new Date().toISOString();

    await createUser({
      username: defaultUsername,
      fullName: defaultFullName,
      email: defaultEmail,
      password: defaultPassword,
      acceptedPoliciesAt: nowIso,
    });
  })();

  await authStore.bootstrapPromise;
}

export async function registerUser(input: RegisterUserInput): Promise<PublicUser> {
  await ensureBootstrapUser();
  const usernameKey = normalizeUsername(input.username);
  if (authStore.usersByKey.has(usernameKey)) {
    throw new Error("user_already_exists");
  }

  const user = await createUser(input);
  return toPublicUser(user);
}

export async function ensureDemoUser(): Promise<PublicUser> {
  if (authStore.demoPromise) {
    return authStore.demoPromise;
  }

  authStore.demoPromise = (async () => {
    await ensureBootstrapUser();
    const demoUsername = process.env.UI_AUTH_DEMO_USERNAME ?? "demo_operator";
    const demoKey = normalizeUsername(demoUsername);
    const existing = authStore.usersByKey.get(demoKey);
    if (existing) {
      return toPublicUser(existing);
    }

    const nowIso = new Date().toISOString();
    const demoEmail = process.env.UI_AUTH_DEMO_EMAIL ?? "demo@spectrastrike.local";
    const demoFullName = process.env.UI_AUTH_DEMO_FULL_NAME ?? "Demo Operator";
    const demoPassword = process.env.UI_AUTH_DEMO_PASSWORD ?? `Demo!${randomBytes(6).toString("hex")}A1`;

    const user = await createUser({
      username: demoUsername,
      fullName: demoFullName,
      email: demoEmail,
      password: demoPassword,
      acceptedPoliciesAt: nowIso,
    });
    return toPublicUser(user);
  })();

  return authStore.demoPromise;
}

export async function authenticateUser(
  username: string,
  password: string
): Promise<PublicUser | null> {
  await ensureBootstrapUser();
  const user = authStore.usersByKey.get(normalizeUsername(username));
  if (!user) {
    return null;
  }

  const isValid = await verifyPassword(password, user.passwordSaltHex, user.passwordHashHex);
  if (!isValid) {
    return null;
  }

  return toPublicUser(user);
}

export function issueSessionToken(userId: string): { accessToken: string; expiresAt: string; maxAge: number } {
  const accessToken = randomBytes(32).toString("base64url");
  const expiresAtMs = Date.now() + sessionTtlSeconds * 1000;
  authStore.sessionsByToken.set(accessToken, {
    token: accessToken,
    userId,
    expiresAtMs,
  });
  return {
    accessToken,
    expiresAt: new Date(expiresAtMs).toISOString(),
    maxAge: sessionTtlSeconds,
  };
}

function pruneExpiredSessions(): void {
  const now = Date.now();
  for (const [token, session] of authStore.sessionsByToken.entries()) {
    if (session.expiresAtMs <= now) {
      authStore.sessionsByToken.delete(token);
    }
  }
}

export function isSessionTokenValid(token: string): boolean {
  pruneExpiredSessions();
  const session = authStore.sessionsByToken.get(token);
  if (!session) {
    return false;
  }
  if (session.expiresAtMs <= Date.now()) {
    authStore.sessionsByToken.delete(token);
    return false;
  }
  return true;
}

export function extractSessionToken(request: Request): string | null {
  const authorization = request.headers.get("authorization") ?? "";
  const [scheme, bearerToken] = authorization.split(" ");
  if (scheme?.toLowerCase() === "bearer" && bearerToken) {
    return bearerToken.trim();
  }

  const cookieHeader = request.headers.get("cookie") ?? "";
  const token = cookieHeader.match(/(?:^|;\s*)spectrastrike_session=([^;]+)/)?.[1];
  return token ? token.trim() : null;
}

export async function isAuthenticatedRequest(request: Request): Promise<boolean> {
  const result = await validateAuthenticatedRequest(request);
  return result.ok;
}

export function revokeSession(token: string): void {
  authStore.sessionsByToken.delete(token);
}

export async function validateAuthenticatedRequest(
  request: Request
): Promise<AuthValidationResult> {
  await ensureBootstrapUser();
  const token = extractSessionToken(request);
  if (!token || !isSessionTokenValid(token)) {
    return { ok: false, error: "unauthorized" };
  }

  const legalDecision = await legalEnforcementService.hooks().forAuthMiddleware();
  if (!legalDecision.isCompliant) {
    return {
      ok: false,
      error: "LEGAL_ACCEPTANCE_REQUIRED",
      legal: {
        environment: legalDecision.environment,
        reason: legalDecision.reason,
        requires_reacceptance: legalDecision.requires_reacceptance,
      },
    };
  }

  return { ok: true };
}
