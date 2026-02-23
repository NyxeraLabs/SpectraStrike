type TelemetrySource = "nmap" | "metasploit" | "manual";
type TelemetryStatus = "success" | "info" | "warning" | "critical";

type TelemetryItem = {
  id: string;
  source: TelemetrySource;
  status: TelemetryStatus;
  eventType: string;
  actor: string;
  target: string;
  timestamp: string;
  details: string;
};

const sourceBadgeClass: Record<TelemetrySource, string> = {
  nmap: "text-telemetryGlow border-telemetryDeep/70",
  metasploit: "text-accentGlow border-accentPrimary/50",
  manual: "text-info border-info/50",
};

const statusClass: Record<TelemetryStatus, string> = {
  success: "text-success",
  info: "text-info",
  warning: "text-warning",
  critical: "text-critical",
};

const telemetryItems: TelemetryItem[] = [
  {
    id: "evt-001",
    source: "nmap",
    status: "success",
    eventType: "nmap_scan_completed",
    actor: "scanner-daemon",
    target: "10.0.9.0/24",
    timestamp: "2026-02-23T18:20:31Z",
    details: "hosts=24 open_ports=43 elapsed_ms=1423",
  },
  {
    id: "evt-002",
    source: "metasploit",
    status: "info",
    eventType: "metasploit_session_ingested",
    actor: "msf-rpc-wrapper",
    target: "workspace/redteam-a",
    timestamp: "2026-02-23T18:19:02Z",
    details: "sessions=4 checkpoints=advanced",
  },
  {
    id: "evt-003",
    source: "manual",
    status: "warning",
    eventType: "manual_sync_partial",
    actor: "operator-jmicoli",
    target: "metasploit.remote.operator",
    timestamp: "2026-02-23T18:16:40Z",
    details: "event_page_timeout=true retry_pending=true",
  },
  {
    id: "evt-004",
    source: "metasploit",
    status: "critical",
    eventType: "exploit_dispatch_failed",
    actor: "msf-rpc-wrapper",
    target: "172.16.10.41",
    timestamp: "2026-02-23T18:15:18Z",
    details: "module=exploit/windows/smb/psexec reason=auth_denied",
  },
];

export function TelemetryFeedView() {
  return (
    <section className="flex flex-col gap-4">
      <article className="spectra-panel p-5">
        <h1 className="text-2xl font-bold text-white [font-family:var(--font-display)]">
          Telemetry Feed
        </h1>
        <p className="mt-2 text-sm text-slate-300">
          Unified Nmap, Metasploit, and manual ingestion telemetry stream.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          <label className="text-xs uppercase tracking-wide text-slate-400">
            Source
            <select className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white">
              <option>All</option>
              <option>Nmap</option>
              <option>Metasploit</option>
              <option>Manual</option>
            </select>
          </label>
          <label className="text-xs uppercase tracking-wide text-slate-400">
            Status
            <select className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white">
              <option>All</option>
              <option>Success</option>
              <option>Info</option>
              <option>Warning</option>
              <option>Critical</option>
            </select>
          </label>
          <label className="text-xs uppercase tracking-wide text-slate-400">
            Cursor
            <input
              type="text"
              placeholder="evt-000"
              className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white"
            />
          </label>
          <div className="flex items-end gap-2">
            <button type="button" className="spectra-button-primary px-4 py-2 text-sm font-semibold">
              Apply
            </button>
            <button type="button" className="spectra-button-secondary px-4 py-2 text-sm font-semibold">
              Reset
            </button>
          </div>
        </div>
      </article>

      <article className="spectra-panel p-5">
        <h2 className="text-sm uppercase tracking-[0.2em] text-telemetry">Live Stream</h2>
        <div className="mt-4 space-y-3">
          {telemetryItems.map((item) => (
            <div key={item.id} className="rounded-panel border border-borderSubtle bg-bgPrimary/60 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`rounded-panel border px-2 py-1 text-xs uppercase tracking-wide ${sourceBadgeClass[item.source]}`}>
                  {item.source}
                </span>
                <span className={`text-xs font-semibold uppercase tracking-wide ${statusClass[item.status]}`}>
                  {item.status}
                </span>
                <span className="spectra-mono ml-auto text-xs text-slate-400">{item.timestamp}</span>
              </div>
              <p className="mt-2 spectra-mono text-sm text-white">{item.eventType}</p>
              <p className="mt-1 text-sm text-slate-300">actor={item.actor} target={item.target}</p>
              <p className="mt-1 spectra-mono text-xs text-slate-400">{item.details}</p>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}
