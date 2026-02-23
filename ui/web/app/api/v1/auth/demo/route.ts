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
  validateOrigin,
} from "../../../../lib/request-guards";
import { ensureDemoUser, issueSessionToken } from "../../../../lib/auth-store";

function isDemoEnabled(): boolean {
  return process.env.UI_AUTH_ENABLE_DEMO_LOGIN !== "false";
}

export async function POST(request: Request) {
  const clientKey = `auth-demo:${clientAddressKey(request)}`;
  if (!enforceRateLimitWithWindow(clientKey, 20, 60_000)) {
    return Response.json({ error: "rate_limited" }, { status: 429 });
  }
  if (!validateOrigin(request)) {
    return Response.json({ error: "origin_forbidden" }, { status: 403 });
  }
  if (!isDemoEnabled()) {
    return Response.json({ error: "demo_disabled" }, { status: 403 });
  }

  const demoUser = await ensureDemoUser();
  const { accessToken, expiresAt, maxAge } = issueSessionToken(demoUser.id);
  const cookieSecure = process.env.UI_AUTH_COOKIE_SECURE !== "false";

  const response = NextResponse.json(
    {
      access_token: accessToken,
      expires_at: expiresAt,
      roles: demoUser.roles,
      user: {
        username: demoUser.username,
        full_name: demoUser.fullName,
        email: demoUser.email,
      },
      mode: "demo",
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
