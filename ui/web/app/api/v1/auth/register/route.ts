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

import {
  clientAddressKey,
  enforceRateLimitWithWindow,
  isJsonContentType,
  validateOrigin,
} from "../../../../lib/request-guards";
import { registerUser } from "../../../../lib/auth-store";

type RegisterPayload = {
  username?: string;
  full_name?: string;
  email?: string;
  password?: string;
  password_confirm?: string;
  accepted_license?: boolean;
  accepted_eula?: boolean;
  accepted_aup?: boolean;
  accepted_privacy?: boolean;
  accepted_security_policy?: boolean;
  registration_token?: string;
};

const usernamePattern = /^[a-zA-Z0-9._-]{3,32}$/;
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isStrongPassword(password: string): boolean {
  return (
    password.length >= 12 &&
    /[a-z]/.test(password) &&
    /[A-Z]/.test(password) &&
    /\d/.test(password) &&
    /[^A-Za-z0-9]/.test(password)
  );
}

function normalizeRegistrationPayload(payload: RegisterPayload) {
  return {
    username: (payload.username ?? "").trim(),
    fullName: (payload.full_name ?? "").trim(),
    email: (payload.email ?? "").trim().toLowerCase(),
    password: payload.password ?? "",
    passwordConfirm: payload.password_confirm ?? "",
    acceptedLicense: payload.accepted_license === true,
    acceptedEula: payload.accepted_eula === true,
    acceptedAup: payload.accepted_aup === true,
    acceptedPrivacy: payload.accepted_privacy === true,
    acceptedSecurityPolicy: payload.accepted_security_policy === true,
    registrationToken: (payload.registration_token ?? "").trim(),
  };
}

function validatePayload(payload: ReturnType<typeof normalizeRegistrationPayload>): string | null {
  if (!usernamePattern.test(payload.username)) {
    return "invalid_username";
  }
  if (payload.fullName.length < 2 || payload.fullName.length > 120) {
    return "invalid_full_name";
  }
  if (!emailPattern.test(payload.email) || payload.email.length > 254) {
    return "invalid_email";
  }
  if (!isStrongPassword(payload.password)) {
    return "weak_password";
  }
  if (payload.password !== payload.passwordConfirm) {
    return "password_mismatch";
  }
  if (
    !payload.acceptedLicense ||
    !payload.acceptedEula ||
    !payload.acceptedAup ||
    !payload.acceptedPrivacy ||
    !payload.acceptedSecurityPolicy
  ) {
    return "policies_not_accepted";
  }

  const requiredRegistrationToken = process.env.UI_AUTH_REGISTRATION_TOKEN?.trim();
  if (requiredRegistrationToken && payload.registrationToken !== requiredRegistrationToken) {
    return "invalid_registration_token";
  }
  return null;
}

export async function POST(request: Request) {
  const clientKey = `auth-register:${clientAddressKey(request)}`;
  if (!enforceRateLimitWithWindow(clientKey, 10, 60_000)) {
    return Response.json({ error: "rate_limited" }, { status: 429 });
  }
  if (!validateOrigin(request)) {
    return Response.json({ error: "origin_forbidden" }, { status: 403 });
  }
  if (!isJsonContentType(request)) {
    return Response.json({ error: "unsupported_media_type" }, { status: 415 });
  }

  const body = (await request.json()) as RegisterPayload;
  const payload = normalizeRegistrationPayload(body);
  const validationError = validatePayload(payload);
  if (validationError) {
    return Response.json({ error: validationError }, { status: 400 });
  }

  try {
    const user = await registerUser({
      username: payload.username,
      fullName: payload.fullName,
      email: payload.email,
      password: payload.password,
      acceptedPoliciesAt: new Date().toISOString(),
    });
    return Response.json(
      {
        user,
        status: "registered",
      },
      { status: 201, headers: { "cache-control": "no-store" } }
    );
  } catch (error) {
    if (error instanceof Error && error.message === "user_already_exists") {
      return Response.json({ error: "username_unavailable" }, { status: 409 });
    }
    return Response.json({ error: "registration_failed" }, { status: 500 });
  }
}
