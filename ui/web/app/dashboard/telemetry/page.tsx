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

import { TopNav } from "../../components/top-nav";
import { TelemetryFeedView } from "../../components/telemetry-feed";

export default function DashboardTelemetryPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <TopNav />
      <TelemetryFeedView />
    </main>
  );
}
