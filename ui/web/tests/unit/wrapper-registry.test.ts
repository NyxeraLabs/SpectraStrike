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

import { describe, expect, it } from "vitest";

import { WRAPPER_REGISTRY } from "../../app/lib/wrapper-registry";

describe("wrapper registry surface", () => {
  it("includes the expected backend wrapper keys", () => {
    const keys = new Set(WRAPPER_REGISTRY.map((item) => item.key));
    const required = [
      "nmap",
      "metasploit",
      "sliver",
      "mythic",
      "impacket_psexec",
      "impacket_wmiexec",
      "impacket_smbexec",
      "impacket_secretsdump",
      "impacket_ntlmrelayx",
      "bloodhound_collector",
      "nuclei",
      "prowler",
      "responder",
      "gobuster",
      "ffuf",
      "netcat",
      "netexec",
      "john",
      "wget",
      "burpsuite",
      "amass",
      "sqlmap",
      "subfinder",
      "dnsx",
      "scp",
      "ssh",
      "curl",
    ];
    for (const key of required) {
      expect(keys.has(key)).toBe(true);
    }
  });
});
