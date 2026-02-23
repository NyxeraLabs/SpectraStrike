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

"use client";

import { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";

type AuthMode = "login" | "register";
type StatusTone = "error" | "success" | "info";

const policySections = [
  {
    id: "license",
    title: "Business Source License 1.1",
    body: "This tool is licensed under BSL 1.1. Internal security testing is permitted. Commercial hosting and competing resale are prohibited until the change date.",
    confirmLabel: "I have read and accept the License terms."
  },
  {
    id: "eula",
    title: "End User License Agreement (EULA)",
    body: "You confirm this platform will be used only by authorized operators for approved engagements. Abuse, unauthorized targeting, and policy bypass are forbidden.",
    confirmLabel: "I have read and accept the EULA."
  },
  {
    id: "security",
    title: "Security Policy",
    body: "You must protect credentials, use MFA, maintain audit trails, and report incidents immediately. Access is role-based and all high-risk actions are logged.",
    confirmLabel: "I have read and accept the Security Policy."
  }
] as const;

export default function LoginPage() {
  const router = useRouter();
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [acceptedPolicies, setAcceptedPolicies] = useState({
    license: false,
    eula: false,
    security: false
  });
  const [registrationUnlocked, setRegistrationUnlocked] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusTone, setStatusTone] = useState<StatusTone>("info");
  const [registrationToken, setRegistrationToken] = useState("");
  const [loginForm, setLoginForm] = useState({
    username: "",
    password: "",
    mfaCode: ""
  });
  const [registerForm, setRegisterForm] = useState({
    fullName: "",
    email: "",
    username: "",
    password: "",
    passwordConfirm: ""
  });

  const allPoliciesAccepted =
    acceptedPolicies.license && acceptedPolicies.eula && acceptedPolicies.security;

  const handlePolicyToggle = (policyId: "license" | "eula" | "security") => {
    setAcceptedPolicies((current) => ({
      ...current,
      [policyId]: !current[policyId]
    }));
  };

  const showStatus = (tone: StatusTone, message: string) => {
    setStatusTone(tone);
    setStatusMessage(message);
  };

  const statusClass =
    statusTone === "error"
      ? "border-critical/40 bg-critical/10 text-red-200"
      : statusTone === "success"
      ? "border-success/40 bg-success/10 text-green-200"
      : "border-info/40 bg-info/10 text-blue-200";

  const submitLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setStatusMessage(null);

    try {
      const response = await fetch("/ui/api/v1/auth/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          username: loginForm.username,
          password: loginForm.password,
          mfa_code: loginForm.mfaCode || undefined
        })
      });
      const body = (await response.json()) as { error?: string };

      if (!response.ok) {
        if (body.error === "LEGAL_ACCEPTANCE_REQUIRED") {
          showStatus("info", "Legal acceptance required. Redirecting...");
          router.push("/legal/acceptance");
          router.refresh();
          return;
        }
        const message =
          body.error === "invalid_credentials"
            ? "Invalid username or password."
            : body.error === "invalid_mfa_code"
            ? "Invalid MFA code format."
            : body.error === "rate_limited"
            ? "Too many attempts. Try again in a minute."
            : "Login failed.";
        showStatus("error", message);
        return;
      }

      showStatus("success", "Login successful. Redirecting to dashboard...");
      router.push("/dashboard");
      router.refresh();
    } catch {
      showStatus("error", "Unable to reach authentication service.");
    } finally {
      setIsLoading(false);
    }
  };

  const submitRegistration = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setStatusMessage(null);

    try {
      const response = await fetch("/ui/api/v1/auth/register", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          full_name: registerForm.fullName,
          email: registerForm.email,
          username: registerForm.username,
          password: registerForm.password,
          password_confirm: registerForm.passwordConfirm,
          accepted_license: acceptedPolicies.license,
          accepted_eula: acceptedPolicies.eula,
          accepted_security_policy: acceptedPolicies.security,
          registration_token: registrationToken || undefined
        })
      });
      const body = (await response.json()) as { error?: string };

      if (!response.ok) {
        const messageByCode: Record<string, string> = {
          invalid_username: "Username must be 3-32 chars and only use letters, numbers, dot, underscore, or dash.",
          invalid_full_name: "Full name is required.",
          invalid_email: "Enter a valid email address.",
          weak_password: "Use a stronger password (12+ chars with upper/lowercase, number, symbol).",
          password_mismatch: "Password and confirmation do not match.",
          policies_not_accepted: "You must accept License, EULA, and Security Policy.",
          invalid_registration_token: "Registration token is invalid.",
          username_unavailable: "That username is already taken.",
          rate_limited: "Too many attempts. Try again in a minute."
        };
        showStatus("error", messageByCode[body.error ?? ""] ?? "Registration failed.");
        return;
      }

      showStatus("success", "Registration completed. You can now sign in.");
      setAuthMode("login");
      setRegistrationUnlocked(false);
      setLoginForm((current) => ({ ...current, username: registerForm.username }));
      setRegisterForm({
        fullName: "",
        email: "",
        username: "",
        password: "",
        passwordConfirm: ""
      });
    } catch {
      showStatus("error", "Unable to reach registration service.");
    } finally {
      setIsLoading(false);
    }
  };

  const openDemoShell = async () => {
    setIsLoading(true);
    setStatusMessage(null);
    try {
      const response = await fetch("/ui/api/v1/auth/demo", { method: "POST" });
      const body = (await response.json()) as { error?: string };
      if (!response.ok) {
        const message =
          body.error === "demo_disabled"
            ? "Demo shell is disabled by policy."
            : body.error === "rate_limited"
            ? "Too many demo attempts. Try again in a minute."
            : "Unable to open demo shell.";
        showStatus("error", message);
        return;
      }
      showStatus("success", "Demo shell session ready. Redirecting...");
      router.push("/dashboard");
      router.refresh();
    } catch {
      showStatus("error", "Unable to reach demo authentication service.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl items-center px-6 py-10">
      <section className="grid w-full gap-6 md:grid-cols-[1.2fr_1fr]">
        <article className="spectra-panel bg-surfaceElevated/80 p-8">
          <Image
            src="/ui/assets/spectrastrike-logo.png"
            alt="SpectraStrike logo"
            width={420}
            height={280}
            className="rounded-lg border border-borderSubtle/80"
            priority
          />
          <p className="text-xs uppercase tracking-[0.2em] text-telemetry">Authentication</p>
          <h1 className="mt-3 text-4xl font-bold text-white [font-family:var(--font-display)]">
            Operator Access
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-slate-300">
            Sign in with your SpectraStrike operator credentials. MFA validation and lockout policy
            are enforced by backend AAA controls.
          </p>
          <ul className="mt-6 space-y-2 text-sm text-slate-300">
            <li>• Remote-operator first endpoint model</li>
            <li>• Tamper-evident audit trail on auth events</li>
            <li>• Local-first deployment, no cloud dependencies</li>
          </ul>
        </article>

        <article className="spectra-panel p-6">
          <div className="mb-5 inline-flex w-full rounded-panel border border-borderSubtle p-1">
            <button
              type="button"
              onClick={() => setAuthMode("login")}
              className={`w-1/2 rounded-panel px-3 py-2 text-sm font-semibold ${
                authMode === "login" ? "spectra-button-primary text-white" : "text-slate-300"
              }`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => setAuthMode("register")}
              className={`w-1/2 rounded-panel px-3 py-2 text-sm font-semibold ${
                authMode === "register" ? "spectra-button-primary text-white" : "text-slate-300"
              }`}
            >
              Register
            </button>
          </div>

          {authMode === "login" ? (
            <>
              {statusMessage ? (
                <div className={`mb-4 rounded-panel border px-3 py-2 text-sm ${statusClass}`}>
                  {statusMessage}
                </div>
              ) : null}
              <form className="space-y-4" method="post" action="#" onSubmit={submitLogin}>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="username">
                    Username
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={loginForm.username}
                    onChange={(event) =>
                      setLoginForm((current) => ({ ...current, username: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="operator"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="password">
                    Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    value={loginForm.password}
                    onChange={(event) =>
                      setLoginForm((current) => ({ ...current, password: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="••••••••"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="mfa">
                    MFA Code
                  </label>
                  <input
                    id="mfa"
                    name="mfa"
                    type="text"
                    value={loginForm.mfaCode}
                    onChange={(event) =>
                      setLoginForm((current) => ({ ...current, mfaCode: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="000000"
                  />
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="spectra-button-primary px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isLoading ? "Signing In..." : "Sign In"}
                  </button>
                  <button
                    type="button"
                    disabled={isLoading}
                    onClick={openDemoShell}
                    className="spectra-button-secondary px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isLoading ? "Opening Demo..." : "Demo Shell"}
                  </button>
                </div>
              </form>
              <p className="mt-4 text-xs text-slate-400">
                UI contract target: <span className="spectra-mono">POST /api/v1/auth/login</span>
              </p>
            </>
          ) : !registrationUnlocked ? (
            <div className="space-y-4">
              {statusMessage ? (
                <div className={`rounded-panel border px-3 py-2 text-sm ${statusClass}`}>
                  {statusMessage}
                </div>
              ) : null}
              <div className="rounded-panel border border-borderSubtle bg-bgPrimary/70 p-4">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-telemetry">
                  Registration prerequisites
                </h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  Read and accept all required legal and security controls before creating an account.
                </p>
              </div>

              <div className="max-h-72 space-y-3 overflow-y-auto pr-1">
                {policySections.map((section) => (
                  <div key={section.id} className="rounded-panel border border-borderSubtle bg-bgPrimary/70 p-4">
                    <h3 className="text-sm font-semibold text-white">{section.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{section.body}</p>
                  </div>
                ))}
              </div>

              <div className="space-y-3 rounded-panel border border-borderSubtle bg-bgPrimary/70 p-4 text-sm text-slate-200">
                {policySections.map((section) => (
                  <label key={`${section.id}-checkbox`} className="flex cursor-pointer items-start gap-3">
                    <input
                      type="checkbox"
                      checked={acceptedPolicies[section.id]}
                      onChange={() => handlePolicyToggle(section.id)}
                      className="mt-1 h-4 w-4 rounded border-borderSubtle bg-bgPrimary text-accentPrimary"
                    />
                    <span>{section.confirmLabel}</span>
                  </label>
                ))}
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="registration-token">
                  Registration Token (Optional)
                </label>
                <input
                  id="registration-token"
                  name="registration_token"
                  type="text"
                  value={registrationToken}
                  onChange={(event) => setRegistrationToken(event.target.value)}
                  className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                  placeholder="Required only if policy enforces it"
                />
              </div>

              <button
                type="button"
                disabled={!allPoliciesAccepted}
                onClick={() => {
                  setRegistrationUnlocked(true);
                  setStatusMessage(null);
                }}
                className="spectra-button-primary w-full px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
              >
                Continue to Registration
              </button>
            </div>
          ) : (
            <>
              {statusMessage ? (
                <div className={`mb-4 rounded-panel border px-3 py-2 text-sm ${statusClass}`}>
                  {statusMessage}
                </div>
              ) : null}
              <form className="space-y-4" method="post" action="#" onSubmit={submitRegistration}>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="register-full-name">
                    Full Name
                  </label>
                  <input
                    id="register-full-name"
                    name="full_name"
                    type="text"
                    value={registerForm.fullName}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, fullName: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="Operator Name"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="register-email">
                    Email
                  </label>
                  <input
                    id="register-email"
                    name="email"
                    type="email"
                    value={registerForm.email}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, email: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="operator@company.test"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="register-username">
                    Username
                  </label>
                  <input
                    id="register-username"
                    name="username"
                    type="text"
                    value={registerForm.username}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, username: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="new-operator"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="register-password">
                    Password
                  </label>
                  <input
                    id="register-password"
                    name="password"
                    type="password"
                    value={registerForm.password}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, password: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="Create a strong password"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="register-password-confirm">
                    Confirm Password
                  </label>
                  <input
                    id="register-password-confirm"
                    name="password_confirm"
                    type="password"
                    value={registerForm.passwordConfirm}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, passwordConfirm: event.target.value }))
                    }
                    className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                    placeholder="Repeat password"
                  />
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="spectra-button-primary px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isLoading ? "Registering..." : "Register User"}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setRegistrationUnlocked(false);
                      setStatusMessage(null);
                    }}
                    className="spectra-button-secondary px-4 py-2 text-sm font-semibold"
                  >
                    Review Policies
                  </button>
                </div>
              </form>
              <p className="mt-4 text-xs text-slate-400">
                UI contract target: <span className="spectra-mono">POST /api/v1/auth/register</span>
              </p>
            </>
          )}
        </article>
      </section>
    </main>
  );
}
