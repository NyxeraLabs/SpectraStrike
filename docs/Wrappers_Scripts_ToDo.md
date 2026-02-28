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
| [x] Amass | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] Subfinder | P0 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] dnsx | P0 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Masscan | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] theHarvester | P2 | [ ] | [x] | [ ] | [ ] | [ ] |

Category completion:
- Implementation: 2/6 (33.3%)
- Documentation: 6/6 (100.0%)
- Unit Tests: 2/6 (33.3%)
- Smoke Tests: 2/6 (33.3%)
- Telemetry Validation: 2/6 (33.3%)

## 2) Web & API Offensive (9)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Nuclei | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Gobuster | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] DirBuster | P1 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] Dirsearch | P1 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [x] ffuf | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] sqlmap | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] Katana | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Nikto | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
| [x] BurpSuite | P0 | [x] | [x] | [x] | [x] | [x] |

Category completion:
- Implementation: 5/9 (55.6%)
- Documentation: 8/9 (88.9%)
- Unit Tests: 5/9 (55.6%)
- Smoke Tests: 5/9 (55.6%)
- Telemetry Validation: 5/9 (55.6%)

## 3) Exploitation & Identity (17)

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
| [x] John the Ripper | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Wget | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] SCP | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] SSH | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] Curl | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [x] Mythic | P1 | [ ] | [ ] | [x] | [ ] | [ ] |
| [x] Metasploit | P1 | [x] | [x] | [x] | [x] | [x] |
| [x] Sliver | P1 | [x] | [x] | [x] | [x] | [x] |

Category completion:
- Implementation: 13/17 (76.5%)
- Documentation: 12/17 (70.6%)
- Unit Tests: 13/17 (76.5%)
- Smoke Tests: 12/17 (70.6%)
- Telemetry Validation: 12/17 (70.6%)

## 4) Cloud & Enterprise Attack Surface (6)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Prowler | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] ScoutSuite | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] CloudFox | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] RoadRecon | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [x] NetExec | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] Azure CLI Security Wrapper | P2 | [ ] | [x] | [ ] | [ ] | [ ] |

Category completion:
- Implementation: 2/6 (33.3%)
- Documentation: 6/6 (100.0%)
- Unit Tests: 2/6 (33.3%)
- Smoke Tests: 2/6 (33.3%)
- Telemetry Validation: 2/6 (33.3%)

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
- [x] Amass full wrapper docs set created
- [x] Gobuster full wrapper docs set created
- [x] ffuf full wrapper docs set created
- [x] BurpSuite full wrapper docs set created
- [x] sqlmap full wrapper docs set created
- [x] Prowler full wrapper docs set created
- [x] Responder full wrapper docs set created
- [x] Netcat full wrapper docs set created
- [x] NetExec full wrapper docs set created
- [x] John the Ripper full wrapper docs set created
- [x] Wget full wrapper docs set created
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
- Amass
- Gobuster
- ffuf
- BurpSuite
- Prowler
- Responder
- Netcat
- NetExec
- John the Ripper
- Wget
- Mythic (implementation and unit tests complete; full E2E pending)

Remaining P0 wrappers:
- Subfinder
- dnsx
- SCP
- SSH
- Curl

Overall completion (current matrix entries):
- Implementation: 22/38 (57.9%)
- Documentation: 32/38 (84.2%)
- Unit Tests: 22/38 (57.9%)
- Smoke Tests: 21/38 (55.3%)
- Telemetry Validation: 21/38 (55.3%)

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
- [x] Amass: host smoke executed (`amass_command_ok=True`) and telemetry emitted (`amass_enum_completed`) with recoverable probe warning path; live E2E currently gated by missing `AMASS_LIVE_TARGET`.
- [x] Nuclei: host smoke executed (`nuclei_command_ok=True`) and telemetry emitted (`nuclei_scan_completed`); live E2E currently gated by missing `NUCLEI_LIVE_TARGET`.
- [x] Gobuster: host smoke executed (`gobuster_command_ok=True`) and telemetry emitted (`gobuster_scan_completed`); live E2E currently gated by missing `GOBUSTER_LIVE_TARGET`.
- [x] ffuf: host smoke executed (`ffuf_command_ok=True`) and telemetry emitted (`ffuf_scan_completed`); live E2E currently gated by missing `FFUF_LIVE_TARGET`.
- [x] BurpSuite: host smoke executed (`burpsuite_command_ok=True`) and telemetry emitted (`burpsuite_session_completed`); live e2e command path validated (`burpsuite.command.live`).
- [x] sqlmap: host smoke executed (`sqlmap_command_ok=True`) and telemetry emitted (`sqlmap_scan_completed`); live e2e command path validated (`sqlmap.command.live`) with `SQLMAP_COMMAND='--version'` and `SQLMAP_COMMAND='--help'`.
- [x] Prowler: host smoke executed (`prowler_command_ok=True`) and telemetry emitted (`prowler_scan_completed`); live E2E currently gated by missing `PROWLER_LIVE_TARGET`.
- [x] Responder: host smoke executed (`responder_command_ok=True`) and telemetry emitted (`responder_session_completed`); live E2E currently gated by missing `RESPONDER_LIVE_INTERFACE`.
- [x] Netcat: host smoke executed (`netcat_command_ok=True`) and telemetry emitted (`netcat_session_completed`); live E2E currently gated by missing `NETCAT_LIVE_TARGET` and `NETCAT_LIVE_PORT`.
- [x] NetExec: host smoke executed (`netexec_command_ok=True`) and telemetry emitted (`netexec_session_completed`); live E2E currently gated by missing `NETEXEC_LIVE_TARGET`, `NETEXEC_LIVE_USERNAME`, and `NETEXEC_LIVE_PASSWORD`.
- [x] John the Ripper: host smoke executed with `JOHN_BINARY=/opt/john/run/john` (`john_command_ok=True`) and telemetry emitted (`john_session_completed`); live e2e command path validated (`john.command.live`).
- [x] Wget: host smoke executed (`wget_command_ok=True`) and telemetry emitted (`wget_session_completed`); live e2e command path validated (`wget.command.live`).
- [x] Sliver: host smoke command path executed (`sliver_binary_ok=True`, `sliver_command_ok=True`) when run outside sandbox restrictions.
- [x] Mythic: wrapper implementation and unit tests are present; full host smoke and live E2E remain blocked in this environment (`mythic-cli` missing on host PATH).
- [ ] Metasploit RPC live auth: blocked by unresolved default RPC endpoint (`metasploit.remote.operator`) until local RPC endpoint is configured.
