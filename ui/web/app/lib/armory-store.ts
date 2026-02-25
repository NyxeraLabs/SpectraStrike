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

type ArmoryItem = {
  tool_name: string;
  image_ref: string;
  tool_sha256: string;
  sbom_status: "queued" | "completed";
  vuln_scan_status: "queued" | "completed";
  signature_status: "pending_approval" | "approved";
  authorized: boolean;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
};

type ArmoryData = {
  items: ArmoryItem[];
};

const storeKey = "__spectrastrikeArmoryStore__";
const existing = (globalThis as Record<string, unknown>)[storeKey] as ArmoryData | undefined;
const armoryStore: ArmoryData = existing ?? { items: [] };
if (!existing) {
  (globalThis as Record<string, unknown>)[storeKey] = armoryStore;
}

function stableSha256Like(input: string): string {
  let hash = 2166136261;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  const hex = (hash >>> 0).toString(16).padStart(8, "0");
  return `sha256:${hex.repeat(8)}`;
}

export function ingestArmoryItem(toolName: string, imageRef: string): ArmoryItem {
  const digest = stableSha256Like(`${toolName}:${imageRef}`);
  const record: ArmoryItem = {
    tool_name: toolName,
    image_ref: imageRef,
    tool_sha256: digest,
    sbom_status: "completed",
    vuln_scan_status: "completed",
    signature_status: "pending_approval",
    authorized: false,
    created_at: new Date().toISOString(),
  };
  armoryStore.items = armoryStore.items.filter((item) => item.tool_sha256 !== digest);
  armoryStore.items.push(record);
  return record;
}

export function approveArmoryItem(toolSha256: string, approver: string): ArmoryItem | null {
  const item = armoryStore.items.find((candidate) => candidate.tool_sha256 === toolSha256);
  if (!item) {
    return null;
  }
  item.signature_status = "approved";
  item.authorized = true;
  item.approved_by = approver;
  item.approved_at = new Date().toISOString();
  return item;
}

export function listAuthorizedArmoryItems(): ArmoryItem[] {
  return armoryStore.items.filter((item) => item.authorized);
}
