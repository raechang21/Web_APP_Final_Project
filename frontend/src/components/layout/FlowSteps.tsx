import { Link, useLocation } from "react-router-dom";

import { FLOW_STEPS } from "@/lib/personality";
import { cn } from "@/lib/utils";

export function FlowSteps() {
  const location = useLocation();

  return (
    <div className="grid gap-3 rounded-[28px] border border-stone-200 bg-[rgba(255,253,250,0.8)] p-4 shadow-soft sm:grid-cols-6">
      {FLOW_STEPS.map((step, index) => {
        const active = location.pathname === step.path;
        const completed = FLOW_STEPS.findIndex((item) => item.path === location.pathname) > index;
        return (
          <Link
            key={step.path}
            to={step.path}
            className={cn(
              "rounded-2xl px-3 py-3 text-sm transition",
              active && "bg-ink text-paper",
              completed && !active && "bg-sky-50 text-accent",
              !active && !completed && "bg-stone-50 text-stone-500 hover:bg-stone-100",
            )}
          >
            <div className="text-xs uppercase tracking-[0.24em] opacity-70">
              {String(index + 1).padStart(2, "0")}
            </div>
            <div className="mt-1 font-medium">{step.label}</div>
          </Link>
        );
      })}
    </div>
  );
}
