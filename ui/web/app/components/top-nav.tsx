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
import Link from "next/link";
import { useRouter } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/telemetry", label: "Telemetry" },
  { href: "/dashboard/armory", label: "Armory" },
  { href: "/dashboard/fleet", label: "Fleet" },
  { href: "/dashboard/policy-trust", label: "Policy & Trust" },
];

export function TopNav() {
  const router = useRouter();
  const [signingOut, setSigningOut] = useState(false);

  const handleSignOut = async () => {
    if (signingOut) {
      return;
    }
    setSigningOut(true);
    try {
      await fetch("/ui/api/v1/auth/logout", { method: "POST" });
    } finally {
      router.push("/login");
      router.refresh();
      setSigningOut(false);
    }
  };

  return (
    <nav className="spectra-panel flex flex-col items-start gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2">
          <Image
            src="/ui/assets/spectrastrike-logo.png"
            alt="SpectraStrike logo"
            width={144}
            height={96}
            className="rounded-md border border-borderSubtle/80"
            priority
          />
          <p className="text-xs uppercase tracking-[0.2em] text-telemetry">SpectraStrike</p>
        </div>
        <p className="mt-1 text-sm text-slate-300">Infrastructure Control Plane</p>
      </div>
      <ul className="flex w-full flex-wrap items-center gap-2 sm:w-auto sm:justify-end">
        {navItems.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              className="spectra-button-secondary inline-flex px-3 py-2 text-xs font-semibold"
            >
              {item.label}
            </Link>
          </li>
        ))}
        <li>
          <button
            type="button"
            onClick={handleSignOut}
            disabled={signingOut}
            className="spectra-button-secondary inline-flex px-3 py-2 text-xs font-semibold disabled:cursor-not-allowed disabled:opacity-60"
          >
            {signingOut ? "Signing Out..." : "Sign Out"}
          </button>
        </li>
      </ul>
    </nav>
  );
}
