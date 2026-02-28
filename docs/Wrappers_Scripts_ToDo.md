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
| [ ] Gobuster | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] DirBuster | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] Dirsearch | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] ffuf | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] sqlmap | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Katana | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] Nikto | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] BurpSuite | P2 | [ ] | [x] | [ ] | [ ] | [ ] |

Category completion:
- Implementation: 1/9 (11.1%)
- Documentation: 7/9 (77.8%)
- Unit Tests: 1/9 (11.1%)
- Smoke Tests: 1/9 (11.1%)
- Telemetry Validation: 1/9 (11.1%)

## 3) Exploitation & Identity (12)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Impacket psexec.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket wmiexec.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket smbexec.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket secretsdump.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] Impacket ntlmrelayx.py | P0 | [x] | [x] | [x] | [x] | [x] |
| [x] BloodHound Collector | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] Responder | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] Netcat | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] Hashcat | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] John the Ripper | P0 | [ ] | [ ] | [ ] | [ ] | [ ] |
| [x] Metasploit | P1 | [x] | [x] | [x] | [x] | [x] |
| [x] Sliver | P1 | [x] | [x] | [x] | [x] | [x] |

Category completion:
- Implementation: 8/12 (66.7%)
- Documentation: 8/12 (66.7%)
- Unit Tests: 8/12 (66.7%)
- Smoke Tests: 8/12 (66.7%)
- Telemetry Validation: 8/12 (66.7%)

## 4) Cloud & Enterprise Attack Surface (6)

| Wrapper | Priority | Impl | Docs | Unit Tests | Smoke Tests | Telemetry Validation |
|---|---|---|---|---|---|---|
| [x] Prowler | P0 | [x] | [x] | [x] | [x] | [x] |
| [ ] ScoutSuite | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] CloudFox | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] RoadRecon | P1 | [ ] | [x] | [ ] | [ ] | [ ] |
| [ ] CrackMapExec | P2 | [ ] | [x] | [ ] | [ ] | [ ] |
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
- [x] Impacket secretsdump.py full wrapper docs set created
- [x] Impacket ntlmrelayx.py full wrapper docs set created
- [x] BloodHound Collector full wrapper docs set created
- [x] Nuclei full wrapper docs set created
- [x] Prowler full wrapper docs set created
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
- Prowler

Remaining P0 wrappers:
- Responder
- Netcat
- Hashcat
- John the Ripper
- Gobuster
- DirBuster
- Dirsearch

Overall completion (current matrix entries):
- Implementation: 11/33 (33.3%)
- Documentation: 27/33 (81.8%)
- Unit Tests: 11/33 (33.3%)
- Smoke Tests: 11/33 (33.3%)
- Telemetry Validation: 11/33 (33.3%)

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
- [x] Prowler: host smoke executed (`prowler_command_ok=True`) and telemetry emitted (`prowler_scan_completed`); live E2E currently gated by missing `PROWLER_LIVE_TARGET`.
- [x] Sliver: host smoke command path executed (`sliver_binary_ok=True`, `sliver_command_ok=True`) when run outside sandbox restrictions.
- [ ] Mythic: blocked in this environment (`mythic-cli` missing on host PATH).
- [ ] Metasploit RPC live auth: blocked by unresolved default RPC endpoint (`metasploit.remote.operator`) until local RPC endpoint is configured.
