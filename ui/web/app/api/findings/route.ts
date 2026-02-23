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

import { findings } from "../../components/findings-data";
import { isAuthenticatedRequest } from "../../lib/auth-store";

export async function GET(request: Request) {
  if (!(await isAuthenticatedRequest(request))) {
    return Response.json({ error: "unauthorized" }, { status: 401 });
  }
  return Response.json({ items: findings, next_cursor: null });
}
