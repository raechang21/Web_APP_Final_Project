import { useEffect, useRef, useState } from "react";
import type { PropsWithChildren, ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";

import { restartSession } from "@/api/session";
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
              <p className="font-display text-2xl">Beyond Personality Labels</p>
              <p className="text-sm text-stone-500">
                從多元人格測驗到諮詢小助手＜(´⌯ ̫⌯`)＞
              </p>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <nav className="flex items-center gap-2 text-sm text-stone-500">
              <NavItem to="/results" locked={!hasResults}>Results</NavItem>
              <NavItem to="/deep-analysis" locked={!hasResults}>Deep Analysis</NavItem>
              <NavItem to="/chatbot" locked={!hasResults}>Chatbot</NavItem>
            </nav>
            <UserMenu />
          </div>
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

function UserMenu() {
  const navigate = useNavigate();
  const userName = useSessionStore((state) => state.user_name);
  const clear = useSessionStore((state) => state.clear);

  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // 點選單外面自動收起
  useEffect(() => {
    if (!open) return;
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  // 沒登入時不顯示頭像
  if (!userName) return null;

  async function handleLogout() {
    try {
      await restartSession();
    } catch {
      // 後端失敗時仍清前端 state，避免使用者卡在「以為已登出但其實沒」的狀態
    }
    clear();
    setOpen(false);
    navigate("/");
  }

  return (
    <div ref={menuRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex h-11 w-11 items-center justify-center rounded-full bg-stone-100 text-base font-medium text-ink transition hover:bg-stone-200"
        aria-label={`使用者選單，當前登入為 ${userName}`}
        aria-expanded={open}
      >
        {userName.charAt(0).toUpperCase()}
      </button>

      {open ? (
        <div className="absolute right-0 top-full z-50 mt-2 w-64 origin-top-right rounded-2xl border border-stone-200 bg-[rgba(255,253,250,0.98)] p-5 shadow-soft backdrop-blur">
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="absolute right-3 top-3 flex h-7 w-7 items-center justify-center rounded-full text-stone-400 transition hover:bg-stone-100 hover:text-ink"
            aria-label="關閉選單"
          >
            ✕
          </button>

          <div className="flex flex-col items-center pt-1">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-stone-100 text-3xl">
              😊
            </div>
            <p className="mt-3 text-sm text-ink">
              <span className="font-medium">{userName}</span>
              ，你好！
            </p>
          </div>

          <div className="mt-4 border-t border-stone-100 pt-3">
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center justify-center gap-1.5 rounded-xl px-3 py-1.5 text-sm text-stone-600 transition hover:bg-red-50 hover:text-red-600"
            >
              <span>登出</span>
            </button>
          </div>
        </div>
      ) : null}
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
  description?: string;
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