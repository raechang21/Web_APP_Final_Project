import type { PropsWithChildren, ReactNode } from "react";
import { Link } from "react-router-dom";

import { cn } from "@/lib/utils";

export function PageShell({
  children,
  className,
}: PropsWithChildren<{ className?: string }>) {
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
            <Link className="rounded-full px-3 py-2 hover:bg-white/70 hover:text-ink" to="/results">
              Results
            </Link>
            <Link className="rounded-full px-3 py-2 hover:bg-white/70 hover:text-ink" to="/deep-analysis">
              Deep Analysis
            </Link>
            <Link className="rounded-full px-3 py-2 hover:bg-white/70 hover:text-ink" to="/chatbot">
              Chatbot
            </Link>
          </nav>
        </header>
        <main className={cn("space-y-6", className)}>{children}</main>
      </div>
    </div>
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
            <p className="max-w-3xl text-base leading-8 text-stone-600 sm:text-lg">
              {description}
            </p>
          </div>
        </div>
        {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
      </div>
    </section>
  );
}
