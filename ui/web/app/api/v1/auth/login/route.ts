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

import { NextResponse } from "next/server";
import {
  clientAddressKey,
  enforceRateLimitWithWindow,
  isJsonContentType,
  validateOrigin,
} from "../../../../lib/request-guards";
import { authenticateUser, issueSessionToken } from "../../../../lib/auth-store";

type LoginPayload = {
  username?: string;
  password?: string;
  mfa_code?: string;
};

function validatePayload(payload: LoginPayload): string | null {
  const username = (payload.username ?? "").trim();
  const password = payload.password ?? "";
  const mfaCode = (payload.mfa_code ?? "").trim();

  if (username.length < 3 || username.length > 64) {
    return "invalid_credentials";
  }
  if (password.length < 8 || password.length > 256) {
    return "invalid_credentials";
  }
  if (mfaCode && !/^\d{6,8}$/.test(mfaCode)) {
    return "invalid_mfa_code";
  }
  return null;
}

export async function POST(request: Request) {
  const clientKey = `auth-login:${clientAddressKey(request)}`;
  if (!enforceRateLimitWithWindow(clientKey, 20, 60_000)) {
    return Response.json({ error: "rate_limited" }, { status: 429 });
  }
  if (!validateOrigin(request)) {
    return Response.json({ error: "origin_forbidden" }, { status: 403 });
  }
  if (!isJsonContentType(request)) {
    return Response.json({ error: "unsupported_media_type" }, { status: 415 });
  }

  const payload = (await request.json()) as LoginPayload;
  const validationError = validatePayload(payload);
  if (validationError) {
    return Response.json({ error: validationError }, { status: 400 });
  }

  const user = await authenticateUser(payload.username ?? "", payload.password ?? "");
  if (!user) {
    return Response.json({ error: "invalid_credentials" }, { status: 401 });
  }

  const { accessToken, expiresAt, maxAge } = issueSessionToken(user.id);
  const cookieSecure = process.env.UI_AUTH_COOKIE_SECURE !== "false";
  const response = NextResponse.json(
    {
      access_token: accessToken,
      expires_at: expiresAt,
      roles: user.roles,
      user: {
        username: user.username,
        full_name: user.fullName,
        email: user.email,
      },
    },
    {
      status: 200,
      headers: { "cache-control": "no-store" },
    }
  );

  response.cookies.set({
    name: "spectrastrike_session",
    value: accessToken,
    maxAge,
    httpOnly: true,
    sameSite: "strict",
    secure: cookieSecure,
    path: "/",
  });

  return response;
}
