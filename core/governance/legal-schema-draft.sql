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

-- Enterprise on-prem installation-level acceptance
CREATE TABLE IF NOT EXISTS legal_installation_acceptance (
  id UUID PRIMARY KEY,
  installation_id TEXT NOT NULL,
  environment TEXT NOT NULL CHECK (environment IN ('enterprise')),
  eula_version TEXT NOT NULL,
  aup_version TEXT NOT NULL,
  accepted_by TEXT NOT NULL,
  accepted_at TIMESTAMPTZ NOT NULL
);

-- Future SaaS user-level acceptance
CREATE TABLE IF NOT EXISTS legal_user_acceptance (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  eula_version TEXT NOT NULL,
  aup_version TEXT NOT NULL,
  privacy_version TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  region TEXT NOT NULL,
  accepted_at TIMESTAMPTZ NOT NULL,
  user_agent TEXT NOT NULL
);
