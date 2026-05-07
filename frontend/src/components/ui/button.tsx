import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "accent";

const styles: Record<Variant, string> = {
  primary:
    "bg-ink text-paper shadow-soft hover:-translate-y-0.5 hover:bg-stone-800",
  secondary:
    "bg-paper text-ink ring-1 ring-stone-200 hover:-translate-y-0.5 hover:bg-stone-50",
  ghost: "bg-transparent text-stone-600 hover:bg-stone-100 hover:text-ink",
  accent:
    "bg-accent text-white shadow-soft hover:-translate-y-0.5 hover:bg-sky-700",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({
  className,
  variant = "primary",
  children,
  ...props
}: PropsWithChildren<ButtonProps>) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-2xl px-4 py-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50",
        styles[variant],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
