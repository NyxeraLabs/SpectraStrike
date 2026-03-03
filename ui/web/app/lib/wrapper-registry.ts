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

import type { ExecutionNodeType } from "./workflow-graph";

export type WrapperDescriptor = {
  key: string;
  label: string;
  category: "recon" | "exploit" | "post_exploit" | "c2" | "credential" | "cloud" | "network" | "web";
  nodeType: ExecutionNodeType;
  description: string;
};

export const WRAPPER_REGISTRY: WrapperDescriptor[] = [
  { key: "nmap", label: "Nmap", category: "recon", nodeType: "initial_access", description: "Network scan and service fingerprinting." },
  { key: "metasploit", label: "Metasploit RPC", category: "exploit", nodeType: "privilege_escalation", description: "Exploit execution and session management." },
  { key: "sliver", label: "Sliver", category: "c2", nodeType: "c2", description: "C2 command execution via Sliver." },
  { key: "mythic", label: "Mythic", category: "c2", nodeType: "c2", description: "Mythic task dispatch wrapper." },
  { key: "impacket_psexec", label: "Impacket PsExec", category: "post_exploit", nodeType: "lateral_movement", description: "Remote command execution via PsExec." },
  { key: "impacket_wmiexec", label: "Impacket WMIExec", category: "post_exploit", nodeType: "lateral_movement", description: "Remote command execution via WMI." },
  { key: "impacket_smbexec", label: "Impacket SMBExec", category: "post_exploit", nodeType: "lateral_movement", description: "SMB-based command execution." },
  { key: "impacket_secretsdump", label: "Impacket SecretsDump", category: "credential", nodeType: "exfiltration", description: "Credential extraction and secrets dumping." },
  { key: "impacket_ntlmrelayx", label: "Impacket NTLMRelayX", category: "credential", nodeType: "lateral_movement", description: "NTLM relay workflow execution." },
  { key: "bloodhound_collector", label: "BloodHound Collector", category: "recon", nodeType: "lateral_movement", description: "AD graph data collection for attack pathing." },
  { key: "nuclei", label: "Nuclei", category: "web", nodeType: "initial_access", description: "Template-driven vulnerability scanning." },
  { key: "prowler", label: "Prowler", category: "cloud", nodeType: "initial_access", description: "Cloud posture and controls assessment." },
  { key: "responder", label: "Responder", category: "credential", nodeType: "lateral_movement", description: "LLMNR/NBT-NS poisoning and credential capture." },
  { key: "gobuster", label: "Gobuster", category: "recon", nodeType: "initial_access", description: "Directory and virtual host enumeration." },
  { key: "ffuf", label: "FFUF", category: "recon", nodeType: "initial_access", description: "Fast web fuzzing and content discovery." },
  { key: "netcat", label: "Netcat", category: "network", nodeType: "c2", description: "Network socket interaction and pivot support." },
  { key: "netexec", label: "NetExec", category: "post_exploit", nodeType: "lateral_movement", description: "SMB/WinRM protocol execution surface." },
  { key: "john", label: "John the Ripper", category: "credential", nodeType: "privilege_escalation", description: "Offline password cracking workflow." },
  { key: "wget", label: "Wget", category: "network", nodeType: "initial_access", description: "Payload retrieval and endpoint probing." },
  { key: "burpsuite", label: "Burp Suite", category: "web", nodeType: "initial_access", description: "Web proxy-assisted attack testing." },
  { key: "amass", label: "Amass", category: "recon", nodeType: "initial_access", description: "Attack surface asset enumeration." },
  { key: "sqlmap", label: "SQLMap", category: "web", nodeType: "privilege_escalation", description: "SQL injection exploitation pipeline." },
  { key: "subfinder", label: "Subfinder", category: "recon", nodeType: "initial_access", description: "Subdomain enumeration for external surface." },
  { key: "dnsx", label: "DNSX", category: "recon", nodeType: "initial_access", description: "DNS probing and validation tasks." },
  { key: "scp", label: "SCP", category: "network", nodeType: "exfiltration", description: "Secure file transfer and extraction tasks." },
  { key: "ssh", label: "SSH", category: "network", nodeType: "lateral_movement", description: "Remote interactive command execution." },
  { key: "curl", label: "cURL", category: "network", nodeType: "initial_access", description: "HTTP request execution and transport probing." },
];
