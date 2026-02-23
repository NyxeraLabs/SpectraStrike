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

export const LegalVersions = {
  EULA: "2026.1",
  AUP: "2026.1",
  PRIVACY: "2026.1",
} as const;

export type LegalDocumentVersionKey = keyof typeof LegalVersions;
