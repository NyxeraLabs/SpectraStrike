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

export async function proxyToOrchestrator(
  path: string,
  init?: RequestInit
): Promise<Response | null> {
  const baseUrl = process.env.ORCHESTRATOR_API_BASE_URL;
  if (!baseUrl) {
    return null;
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  try {
    const target = `${baseUrl.replace(/\/$/, "")}${path}`;
    const response = await fetch(target, {
      ...init,
      signal: controller.signal,
      headers: {
        "content-type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
    return response;
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}
