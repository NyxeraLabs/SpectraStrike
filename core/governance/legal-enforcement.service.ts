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

import { randomUUID } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

import { LegalVersions } from "../../config/legal.config";

export type DeploymentEnvironment = "self-hosted" | "enterprise" | "saas";
export type LegalDocumentKey = "eula" | "aup" | "privacy";

export type LegalAcceptanceRecord = {
  environment: DeploymentEnvironment;
  installation_id?: string;
  user_id?: string;
  accepted_documents: Partial<Record<LegalDocumentKey, string>>;
  accepted_at: string;
  accepted_by?: string;
  ip_address?: string;
  region?: string;
  user_agent?: string;
};

export type LegalEnforcementDecision = {
  environment: DeploymentEnvironment;
  isCompliant: boolean;
  errorCode?: "LEGAL_ACCEPTANCE_REQUIRED";
  reason?: string;
  required_versions: Record<LegalDocumentKey, string>;
  accepted_versions: Partial<Record<LegalDocumentKey, string>>;
  requires_reacceptance: boolean;
};

export type LegalEnforcementContext = {
  environment?: DeploymentEnvironment;
  acceptanceRecord?: LegalAcceptanceRecord | null;
};

export class LegalAcceptanceRequiredError extends Error {
  public readonly code = "LEGAL_ACCEPTANCE_REQUIRED";

  constructor(message: string) {
    super(message);
  }
}

export class LegalEnforcementService {
  private readonly requiredVersions: Record<LegalDocumentKey, string>;
  private readonly acceptancePath: string;
  private readonly requirePerUserEnterprise: boolean;

  constructor() {
    this.requiredVersions = {
      eula: LegalVersions.EULA,
      aup: LegalVersions.AUP,
      privacy: LegalVersions.PRIVACY,
    };
    this.acceptancePath = path.resolve(
      process.cwd(),
      process.env.SPECTRASTRIKE_LEGAL_ACCEPTANCE_PATH ??
        ".spectrastrike/legal/acceptance.json"
    );
    this.requirePerUserEnterprise =
      process.env.SPECTRASTRIKE_ENTERPRISE_REQUIRE_PER_USER_ACCEPTANCE === "true";
  }

  detectEnvironment(): DeploymentEnvironment {
    const rawValue = (process.env.SPECTRASTRIKE_ENV ?? "self-hosted").trim();
    if (
      rawValue === "self-hosted" ||
      rawValue === "enterprise" ||
      rawValue === "saas"
    ) {
      return rawValue;
    }
    return "self-hosted";
  }

  async evaluate(
    context: LegalEnforcementContext = {}
  ): Promise<LegalEnforcementDecision> {
    const environment = context.environment ?? this.detectEnvironment();
    const requiredDocuments = this.requiredDocumentsForEnvironment(environment);
    const accepted =
      context.acceptanceRecord ?? (await this.loadAcceptanceForEnvironment(environment));

    if (!accepted) {
      this.audit("legal_enforcement_block", {
        environment,
        reason: "no acceptance record found",
      });
      return {
        environment,
        isCompliant: false,
        errorCode: "LEGAL_ACCEPTANCE_REQUIRED",
        reason: "no acceptance record found",
        required_versions: this.requiredVersions,
        accepted_versions: {},
        requires_reacceptance: true,
      };
    }

    const acceptedVersions = accepted.accepted_documents ?? {};
    const staleDocuments = requiredDocuments.filter(
      (doc) => acceptedVersions[doc] !== this.requiredVersions[doc]
    );

    if (staleDocuments.length > 0) {
      this.audit("legal_enforcement_block", {
        environment,
        reason: "outdated acceptance",
        stale_documents: staleDocuments,
      });
      return {
        environment,
        isCompliant: false,
        errorCode: "LEGAL_ACCEPTANCE_REQUIRED",
        reason: `outdated acceptance for ${staleDocuments.join(",")}`,
        required_versions: this.requiredVersions,
        accepted_versions: acceptedVersions,
        requires_reacceptance: true,
      };
    }

    this.audit("legal_enforcement_allow", {
      environment,
      accepted_at: accepted.accepted_at,
    });
    return {
      environment,
      isCompliant: true,
      required_versions: this.requiredVersions,
      accepted_versions: acceptedVersions,
      requires_reacceptance: false,
    };
  }

  async assertEnforced(context: LegalEnforcementContext = {}): Promise<void> {
    const decision = await this.evaluate(context);
    if (!decision.isCompliant) {
      throw new LegalAcceptanceRequiredError(
        decision.reason ?? "legal acceptance is required"
      );
    }
  }

  async recordSelfHostedAcceptance(input: {
    acceptedBy?: string;
    acceptedDocuments: Partial<Record<LegalDocumentKey, string>>;
    installationId?: string;
  }): Promise<LegalAcceptanceRecord> {
    const acceptance: LegalAcceptanceRecord = {
      environment: "self-hosted",
      installation_id: input.installationId ?? randomUUID(),
      accepted_documents: input.acceptedDocuments,
      accepted_at: new Date().toISOString(),
      accepted_by: input.acceptedBy,
    };
    await mkdir(path.dirname(this.acceptancePath), { recursive: true });
    await writeFile(
      this.acceptancePath,
      `${JSON.stringify(acceptance, null, 2)}\n`,
      "utf-8"
    );
    this.audit("legal_acceptance_recorded", {
      environment: "self-hosted",
      installation_id: acceptance.installation_id,
      accepted_by: acceptance.accepted_by,
    });
    return acceptance;
  }

  async loadSelfHostedAcceptance(): Promise<LegalAcceptanceRecord | null> {
    try {
      const raw = await readFile(this.acceptancePath, "utf-8");
      const parsed = JSON.parse(raw) as LegalAcceptanceRecord;
      if (parsed.environment !== "self-hosted") {
        return null;
      }
      if (!parsed.accepted_documents || typeof parsed.accepted_documents !== "object") {
        return null;
      }
      return parsed;
    } catch {
      return null;
    }
  }

  hooks() {
    return {
      forCli: async () => this.evaluate({ environment: this.detectEnvironment() }),
      forWebUi: async () => this.evaluate({ environment: this.detectEnvironment() }),
      forAuthMiddleware: async () =>
        this.evaluate({ environment: this.detectEnvironment() }),
      forRbac: async () => this.evaluate({ environment: this.detectEnvironment() }),
    };
  }

  private requiredDocumentsForEnvironment(
    environment: DeploymentEnvironment
  ): LegalDocumentKey[] {
    if (environment === "saas") {
      return ["eula", "aup", "privacy"];
    }
    if (environment === "enterprise" && this.requirePerUserEnterprise) {
      return ["eula", "aup", "privacy"];
    }
    return ["eula", "aup"];
  }

  private async loadAcceptanceForEnvironment(
    environment: DeploymentEnvironment
  ): Promise<LegalAcceptanceRecord | null> {
    if (environment === "self-hosted") {
      return this.loadSelfHostedAcceptance();
    }
    return null;
  }

  private audit(event: string, fields: Record<string, unknown>): void {
    const payload = {
      event,
      source: "core/governance/legal-enforcement.service",
      timestamp: new Date().toISOString(),
      ...fields,
    };
    console.info(JSON.stringify(payload));
  }
}

const globalKey = "__spectrastrikeLegalEnforcementService__";
const existing = (globalThis as Record<string, unknown>)[globalKey] as
  | LegalEnforcementService
  | undefined;

export const legalEnforcementService =
  existing ?? new LegalEnforcementService();

if (!existing) {
  (globalThis as Record<string, unknown>)[globalKey] = legalEnforcementService;
}
