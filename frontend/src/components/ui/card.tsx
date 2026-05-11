import type { HTMLAttributes, PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
  ...props
}: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div
        className={cn(
        "rounded-[28px] border border-stone-200/80 bg-[rgba(255,253,250,0.9)] shadow-soft backdrop-blur",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardContent({
  className,
  children,
  ...props
}: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div className={cn("p-6", className)} {...props}>
      {children}
    </div>
  );
}
