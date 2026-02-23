import Image from "next/image";
import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/telemetry", label: "Telemetry" },
  { href: "/dashboard/findings", label: "Findings" },
  { href: "/login", label: "Sign Out" },
];

export function TopNav() {
  return (
    <nav className="spectra-panel flex flex-col items-start gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2">
          <Image
            src="/ui/assets/spectrastrike-logo.png"
            alt="SpectraStrike logo"
            width={28}
            height={28}
            className="rounded-md border border-borderSubtle/80"
            priority
          />
          <p className="text-xs uppercase tracking-[0.2em] text-telemetry">SpectraStrike</p>
        </div>
        <p className="mt-1 text-sm text-slate-300">Operator Console</p>
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
      </ul>
    </nav>
  );
}
