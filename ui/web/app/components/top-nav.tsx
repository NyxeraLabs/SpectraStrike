import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard?tab=telemetry", label: "Telemetry" },
  { href: "/dashboard?tab=findings", label: "Findings" },
  { href: "/login", label: "Sign Out" },
];

export function TopNav() {
  return (
    <nav className="spectra-panel flex items-center justify-between px-4 py-3">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-telemetry">SpectraStrike</p>
        <p className="mt-1 text-sm text-slate-300">Operator Console</p>
      </div>
      <ul className="flex flex-wrap items-center gap-2">
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
