const events = [
  {
    event_id: "evt-001",
    source: "nmap",
    status: "success",
    event_type: "nmap_scan_completed",
    actor: "scanner-daemon",
    target: "10.0.9.0/24",
    timestamp: "2026-02-23T18:20:31Z",
  },
  {
    event_id: "evt-002",
    source: "metasploit",
    status: "info",
    event_type: "metasploit_session_ingested",
    actor: "msf-rpc-wrapper",
    target: "workspace/redteam-a",
    timestamp: "2026-02-23T18:19:02Z",
  },
  {
    event_id: "evt-003",
    source: "manual",
    status: "warning",
    event_type: "manual_sync_partial",
    actor: "operator-jmicoli",
    target: "metasploit.remote.operator",
    timestamp: "2026-02-23T18:16:40Z",
  },
];

export async function GET() {
  return Response.json({ items: events, next_cursor: null });
}
