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
import { extractSessionToken, revokeSession } from "../../../../lib/auth-store";

export async function POST(request: Request) {
  const clientKey = `auth-logout:${clientAddressKey(request)}`;
  if (!enforceRateLimitWithWindow(clientKey, 30, 60_000)) {
    return Response.json({ error: "rate_limited" }, { status: 429 });
  }
  if (!validateOrigin(request)) {
    return Response.json({ error: "origin_forbidden" }, { status: 403 });
  }

  const cookieSecure = process.env.UI_AUTH_COOKIE_SECURE !== "false";
  const token = extractSessionToken(request);
  if (token) {
    revokeSession(token);
  }

  const response = new NextResponse(null, { status: 204 });
  response.cookies.set({
    name: "spectrastrike_session",
    value: "",
    maxAge: 0,
    httpOnly: true,
    sameSite: "strict",
    secure: cookieSecure,
    path: "/",
  });
  return response;
}
