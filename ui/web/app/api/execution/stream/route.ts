/*
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
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

import { validateAuthenticatedRequest } from "../../../lib/auth-store";
import { listRuntimeTasks, summarizeRuntimeQueue } from "../../../lib/execution-runtime-store";

const encoder = new TextEncoder();

function sseEvent(event: string, data: unknown): Uint8Array {
  return encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}

export async function GET(request: Request) {
  const authDecision = await validateAuthenticatedRequest(request);
  if (!authDecision.ok) {
    const status = authDecision.error === "LEGAL_ACCEPTANCE_REQUIRED" ? 403 : 401;
    return Response.json({ error: authDecision.error ?? "unauthorized", legal: authDecision.legal }, { status });
  }

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(
        sseEvent("diagnostic", {
          mode: "runtime_store",
          detail: "streaming_local_execution_queue",
          statuses: ["queued", "running", "blocked", "retrying", "failed", "completed"],
        })
      );
      const heartbeat = setInterval(() => {
        controller.enqueue(
          sseEvent("status_snapshot", {
            queue: summarizeRuntimeQueue(),
            items: listRuntimeTasks(50),
          })
        );
        controller.enqueue(
          sseEvent("heartbeat", {
            ts: new Date().toISOString(),
          })
        );
      }, 5000);
      const abort = request.signal;
      abort.addEventListener("abort", () => {
        clearInterval(heartbeat);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "content-type": "text/event-stream",
      "cache-control": "no-store",
      connection: "keep-alive",
    },
  });
}
