import type { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm text-ink outline-none transition placeholder:text-stone-400 focus:border-accent focus:ring-4 focus:ring-sky-100",
        className,
      )}
      {...props}
    />
  );
}
