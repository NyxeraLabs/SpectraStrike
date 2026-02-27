# SpectraStrike Wrapper Matrix (24 Total)
## Checkbox Standard Format

Priority Legend:
- P0 = Foundational / Enterprise-Critical
- P1 = High ROI / Core Coverage
- P2 = Expansion / Extended Coverage

====================================================
1️⃣ Recon & Surface Discovery (6)
====================================================

- [x] (P0) Nmap — Core network discovery (✅ Already Implemented)
- [ ] (P1) Amass — Deep subdomain & ASN enumeration
- [ ] (P1) Subfinder — Passive subdomain discovery
- [ ] (P1) dnsx — DNS validation & enrichment
- [ ] (P2) Masscan — High-speed port scanning
- [ ] (P2) theHarvester — OSINT email/domain enumeration


====================================================
2️⃣ Web & API Offensive (6)
====================================================

- [ ] (P0) Nuclei — Template-based vulnerability scanning
- [ ] (P1) ffuf — Web fuzzing automation
- [ ] (P1) sqlmap — SQL injection exploitation
- [ ] (P1) Katana — Web/API crawler
- [ ] (P2) Nikto — Broad web server scanner
- [ ] (P2) BurpSuite— Automated web/API scanning


====================================================
3️⃣ Exploitation & Identity (6)
====================================================

----------------------------------------
Impacket Wrapper Family (P0)
----------------------------------------

All modules must:
- Emit canonical telemetry
- Embed execution_fingerprint
- Embed attestation_hash
- Sign payload (Ed25519)

- [ ] (P0) Impacket psexec.py — SMB remote execution
- [ ] (P0) Impacket wmiexec.py — WMI remote execution
- [ ] (P0) Impacket smbexec.py — Service-based execution
- [ ] (P0) Impacket secretsdump.py — Credential extraction
- [ ] (P0) Impacket ntlmrelayx.py — NTLM relay automation

----------------------------------------
Additional Identity / C2 Tools
----------------------------------------

- [ ] (P0) BloodHound Collector — AD attack path mapping
- [x] (P1) Metasploit — Modular exploitation framework (✅ Already Implemented)
- [x] (P1) Sliver — Modern C2 framework (✅ Already Implemented)


====================================================
4️⃣ Cloud & Enterprise Attack Surface (6)
====================================================

- [ ] (P0) Prowler — AWS security auditing baseline
- [ ] (P1) ScoutSuite — Multi-cloud posture assessment
- [ ] (P1) CloudFox — Cloud privilege mapping
- [ ] (P1) RoadRecon — Azure AD reconnaissance
- [ ] (P2) CrackMapExec — Credential abuse automation
- [ ] (P2) Azure CLI Security Wrapper — Native cloud assessment integration


====================================================
IMPLEMENTATION STATUS SNAPSHOT
====================================================

Already Implemented:
- Nmap
- Metasploit
- Sliver

Remaining High Priority (P0 not yet done):
- Impacket Family
- BloodHound Collector
- Nuclei
- Prowler

Target:
24 Total Wrappers
4 Categories
6 Per Category
Enterprise-Ready Coverage