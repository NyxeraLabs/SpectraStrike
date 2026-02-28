<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike Wrapper Matrix

Priority Legend:
- P0 = Foundational / Enterprise-Critical
- P1 = High ROI / Core Coverage
- P2 = Expansion / Extended Coverage

## 1) Recon & Surface Discovery (6)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Nmap | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] Amass | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Subfinder | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] dnsx | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Masscan | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] theHarvester | P2 | [ ] | [x] | [ ] | [ ] | [ ] |

Category completion:
- Implementation: 1/6 (16.7%)
- Documentation: 6/6 (100.0%)
- Unit Tests: 1/6 (16.7%)
- Smoke Tests: 1/6 (16.7%)
- Telemetry Validation: 1/6 (16.7%)

## 2) Web & API Offensive (9)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Nuclei | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Gobuster | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] DirBuster | P1 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] Dirsearch | P1 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [x] ffuf | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] sqlmap | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Katana | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Nikto | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] BurpSuite | P0 | [ ] | [x] | [ ] | [ ] | [ ] |

Category completion:
- Implementation: 3/9 (33.3%)
- Documentation: 8/9 (88.9%)
- Unit Tests: 3/9 (33.3%)
- Smoke Tests: 3/9 (33.3%)
- Telemetry Validation: 3/9 (33.3%)

## 3) Exploitation & Identity (13)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Impacket psexec.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket wmiexec.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket smbexec.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket secretsdump.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket ntlmrelayx.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] BloodHound Collector | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Responder | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Netcat | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] Hashcat | P1 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] John the Ripper | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [x] Mythic | P1 | [ ] | [ ] | [x] | [ ] | [ ] |
| [x] Metasploit | P1 | [x] | [x] | [x] | [x] | [x] |
| [x] Sliver | P1 | [x] | [x] | [x] | [x] | [x] |

Category completion:
- Implementation: 11/13 (84.6%)
- Documentation: 10/13 (76.9%)
- Unit Tests: 11/13 (84.6%)
- Smoke Tests: 10/13 (76.9%)
- Telemetry Validation: 10/13 (76.9%)

## 4) Cloud & Enterprise Attack Surface (6)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Prowler | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] ScoutSuite | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] CloudFox | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] RoadRecon | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] NetExec | P0 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Azure CLI Security Wrapper | P2 | [ ] | [x] | [ ] | [ ] | [ ] |

Category completion:
- Implementation: 1/6 (16.7%)
- Documentation: 6/6 (100.0%)
- Unit Tests: 1/6 (16.7%)
- Smoke Tests: 1/6 (16.7%)
- Telemetry Validation: 1/6 (16.7%)

## Documentation Tasks

- [x] Nmap full wrapper docs set created
- [x] Metasploit full wrapper docs set created
- [x] Sliver full wrapper docs set created
- [x] Impacket psexec.py full wrapper docs set created
- [x] Impacket wmiexec.py full wrapper docs set created
- [x] Impacket smbexec.py full wrapper docs set created
- [x] Impacket secretsdump.py full wrapper docs set created
- [x] Impacket ntlmrelayx.py full wrapper docs set created
- [x] BloodHound Collector full wrapper docs set created
- [x] Nuclei full wrapper docs set created
- [x] Gobuster full wrapper docs set created
- [x] ffuf full wrapper docs set created
- [x] Prowler full wrapper docs set created
- [x] Responder full wrapper docs set created
- [x] Netcat full wrapper docs set created
- [ ] Mythic full wrapper docs set created
- [ ] All remaining wrappers documentation scaffolds created
- [x] Wrapper federation E2E audit updated (2026-02-28)

## Standard Procedure (Future Tasks)

For every remaining wrapper, apply this exact sequence:
1. Implement wrapper with standardized SDK contract.
2. Run real E2E test (no dry-run) with controlled target.
3. Add/validate unit tests.
4. Add/validate smoke test.
5. Validate telemetry schema.
6. Create/refresh full docs set under `docs/wrappers/<wrapper>/`.
7. Update this matrix checkboxes and category percentages.

## Global Snapshot

Already implemented in codebase:
- Nmap
- Metasploit
- Sliver
- Impacket psexec.py
- Impacket wmiexec.py
- Impacket smbexec.py
- Impacket secretsdump.py
- Impacket ntlmrelayx.py
- BloodHound Collector
- Nuclei
- Gobuster
- ffuf
- Prowler
- Responder
- Netcat
- Mythic (implementation and unit tests complete; full E2E pending)

Remaining P0 wrappers:
- John the Ripper
- BurpSuite
- NetExec

Overall completion (current matrix entries):
- Implementation: 16/34 (47.1%)
- Documentation: 30/34 (88.2%)
- Unit Tests: 16/34 (47.1%)
- Smoke Tests: 15/34 (44.1%)
- Telemetry Validation: 15/34 (44.1%)

## Latest E2E Federation Audit (2026-02-28)

Implemented wrappers audit status:

- [x] Nmap: host smoke + federation bridge executed (recoverable sendOK warning path handled).
- [x] Metasploit: binary/version + host smoke telemetry path executed.
- [x] Impacket psexec.py: signed execution contract path executed (`impacket_psexec_command_ok=True`) with local key path.
- [x] Impacket wmiexec.py: host smoke executed (`impacket_wmiexec_command_ok=True`) and telemetry emitted (`impacket_wmiexec_completed`); live E2E currently gated by missing `IMPACKET_WMIEXEC_PASSWORD` or `IMPACKET_WMIEXEC_HASHES`.
- [x] Impacket smbexec.py: host smoke executed (`impacket_smbexec_command_ok=True`) and telemetry emitted (`impacket_smbexec_completed`); live E2E currently gated by missing `IMPACKET_SMBEXEC_PASSWORD` or `IMPACKET_SMBEXEC_HASHES`.
- [x] Impacket secretsdump.py: host smoke executed (`impacket_secretsdump_command_ok=True`) and telemetry emitted (`impacket_secretsdump_completed`); live E2E currently gated by missing `IMPACKET_SECRETSDUMP_PASSWORD` or `IMPACKET_SECRETSDUMP_HASHES`.
- [x] Impacket ntlmrelayx.py: host smoke executed (`impacket_ntlmrelayx_command_ok=True`) and telemetry emitted (`impacket_ntlmrelayx_completed`); live E2E currently gated by missing `IMPACKET_NTLMRELAYX_PASSWORD` or `IMPACKET_NTLMRELAYX_HASHES`.
- [x] BloodHound Collector: host smoke executed (`bloodhound_collector_command_ok=True`) and telemetry emitted (`bloodhound_collector_completed`); live E2E currently gated by missing `BLOODHOUND_COLLECTOR_PASSWORD`.
- [x] Nuclei: host smoke executed (`nuclei_command_ok=True`) and telemetry emitted (`nuclei_scan_completed`); live E2E currently gated by missing `NUCLEI_LIVE_TARGET`.
- [x] Gobuster: host smoke executed (`gobuster_command_ok=True`) and telemetry emitted (`gobuster_scan_completed`); live E2E currently gated by missing `GOBUSTER_LIVE_TARGET`.
- [x] ffuf: host smoke executed (`ffuf_command_ok=True`) and telemetry emitted (`ffuf_scan_completed`); live E2E currently gated by missing `FFUF_LIVE_TARGET`.
- [x] Prowler: host smoke executed (`prowler_command_ok=True`) and telemetry emitted (`prowler_scan_completed`); live E2E currently gated by missing `PROWLER_LIVE_TARGET`.
- [x] Responder: host smoke executed (`responder_command_ok=True`) and telemetry emitted (`responder_session_completed`); live E2E currently gated by missing `RESPONDER_LIVE_INTERFACE`.
- [x] Netcat: host smoke executed (`netcat_command_ok=True`) and telemetry emitted (`netcat_session_completed`); live E2E currently gated by missing `NETCAT_LIVE_TARGET` and `NETCAT_LIVE_PORT`.
- [x] Sliver: host smoke command path executed (`sliver_binary_ok=True`, `sliver_command_ok=True`) when run outside sandbox restrictions.
- [x] Mythic: wrapper implementation and unit tests are present; full host smoke and live E2E remain blocked in this environment (`mythic-cli` missing on host PATH).
- [ ] Metasploit RPC live auth: blocked by unresolved default RPC endpoint (`metasploit.remote.operator`) until local RPC endpoint is configured.
