import type { PropsWithChildren, ReactNode } from "react";
import { Link } from "react-router-dom";

import { cn } from "@/lib/utils";
import { useSessionStore } from "@/store/session";

export function PageShell({
  children,
  className,
}: PropsWithChildren<{ className?: string }>) {
  const hasResults = useSessionStore((state) => state.has_results);

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-3 text-ink">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-ink text-paper">
              ✦
            </div>
            <div>
              <p className="font-display text-2xl">Personality Paradox</p>
              <p className="text-sm text-stone-500">React + FastAPI refactor branch</p>
            </div>
          </Link>
          <nav className="flex items-center gap-2 text-sm text-stone-500">
            <NavItem to="/results" locked={!hasResults}>
              Results
            </NavItem>
            <NavItem to="/deep-analysis" locked={!hasResults}>
              Deep Analysis
            </NavItem>
            <NavItem to="/chatbot" locked={!hasResults}>
              Chatbot
            </NavItem>
          </nav>
        </header>
        <main className={cn("space-y-6", className)}>{children}</main>
      </div>
    </div>
  );
}

function NavItem({
  to,
  locked,
  children,
}: {
  to: string;
  locked: boolean;
  children: ReactNode;
}) {
  const base = "rounded-full px-3 py-2 transition";

  if (locked) {
    return (
      <span
        aria-disabled="true"
        title="完成測驗後解鎖"
        className={cn(base, "cursor-not-allowed text-stone-300")}
      >
        {children}
      </span>
    );
  }

  return (
    <Link to={to} className={cn(base, "hover:bg-white/70 hover:text-ink")}>
      {children}
    </Link>
  );
}

export function SectionHero({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
}) {
  return (
    <section className="hero-panel">
      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
        <div className="space-y-4">
          <span className="hero-eyebrow">{eyebrow}</span>
          <div className="space-y-3">
            <h1 className="font-display text-4xl text-ink sm:text-5xl">{title}</h1>
            <p className="text-pretty text-base leading-8 text-stone-600 sm:text-lg">
              {description}
            </p>
          </div>
        </div>
        {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
      </div>
    </section>
  );
}
