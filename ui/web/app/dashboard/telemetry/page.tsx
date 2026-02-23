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
