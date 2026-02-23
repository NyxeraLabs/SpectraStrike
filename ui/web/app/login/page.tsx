import Image from "next/image";
import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl items-center px-6 py-10">
      <section className="grid w-full gap-6 md:grid-cols-[1.2fr_1fr]">
        <article className="spectra-panel bg-surfaceElevated/80 p-8">
          <Image
            src="/ui/assets/spectrastrike-logo.png"
            alt="SpectraStrike logo"
            width={110}
            height={73}
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
          <form className="space-y-4" method="post" action="#">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-300" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
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
                className="mt-2 w-full rounded-panel border border-borderSubtle bg-bgPrimary px-3 py-2 text-sm text-white outline-none ring-0 focus:border-accentFocus"
                placeholder="000000"
              />
            </div>
            <div className="flex items-center gap-2 pt-2">
              <button type="submit" className="spectra-button-primary px-4 py-2 text-sm font-semibold">
                Sign In
              </button>
              <Link href="/dashboard" className="spectra-button-secondary px-4 py-2 text-sm font-semibold">
                Demo Shell
              </Link>
            </div>
          </form>
          <p className="mt-4 text-xs text-slate-400">
            UI contract target: <span className="spectra-mono">POST /api/v1/auth/login</span>
          </p>
        </article>
      </section>
    </main>
  );
}
