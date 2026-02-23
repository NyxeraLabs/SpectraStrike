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

export type FindingSeverity = "low" | "medium" | "high" | "critical";
export type FindingStatus = "open" | "accepted" | "resolved";

export type Finding = {
  finding_id: string;
  title: string;
  severity: FindingSeverity;
  status: FindingStatus;
  source: "nmap" | "metasploit" | "manual";
  target: string;
  created_at: string;
  updated_at: string;
  summary: string;
};

export type EvidenceItem = {
  evidence_id: string;
  type: "log" | "artifact" | "command_output" | "screenshot";
  content_ref: string;
  captured_at: string;
};

export const findings: Finding[] = [
  {
    finding_id: "FND-2026-001",
    title: "SMB signing disabled on perimeter host",
    severity: "high",
    status: "open",
    source: "metasploit",
    target: "172.16.10.41",
    created_at: "2026-02-23T17:41:11Z",
    updated_at: "2026-02-23T18:01:32Z",
    summary: "Host accepts unsigned SMB sessions enabling relay risk.",
  },
  {
    finding_id: "FND-2026-002",
    title: "Legacy TLS cipher suite exposed",
    severity: "medium",
    status: "open",
    source: "nmap",
    target: "10.0.9.22:443",
    created_at: "2026-02-23T16:38:02Z",
    updated_at: "2026-02-23T17:10:47Z",
    summary: "Endpoint still negotiates outdated cipher profile.",
  },
  {
    finding_id: "FND-2026-003",
    title: "Operator-reported weak admin password reuse",
    severity: "critical",
    status: "accepted",
    source: "manual",
    target: "vault-admin",
    created_at: "2026-02-23T15:22:45Z",
    updated_at: "2026-02-23T16:05:13Z",
    summary: "Same credential used across segmented administration zones.",
  },
];

export const evidenceByFindingId: Record<string, EvidenceItem[]> = {
  "FND-2026-001": [
    {
      evidence_id: "EVD-001-A",
      type: "command_output",
      content_ref: "msf://workspace/redteam-a/session/4/output/17",
      captured_at: "2026-02-23T17:42:03Z",
    },
    {
      evidence_id: "EVD-001-B",
      type: "log",
      content_ref: "log://orchestrator/events/evt-004",
      captured_at: "2026-02-23T17:42:21Z",
    },
  ],
  "FND-2026-002": [
    {
      evidence_id: "EVD-002-A",
      type: "artifact",
      content_ref: "nmap://scan/2026-02-23/10.0.9.22/tls-ciphers",
      captured_at: "2026-02-23T16:40:54Z",
    },
  ],
  "FND-2026-003": [
    {
      evidence_id: "EVD-003-A",
      type: "screenshot",
      content_ref: "manual://operator-note/credential-reuse-2026-02-23",
      captured_at: "2026-02-23T15:25:10Z",
    },
  ],
};
