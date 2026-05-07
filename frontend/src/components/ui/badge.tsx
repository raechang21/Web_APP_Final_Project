import type { HTMLAttributes, PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

export function Badge({
  className,
  children,
  ...props
}: PropsWithChildren<HTMLAttributes<HTMLSpanElement>>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full bg-stone-100 px-3 py-1 text-xs font-medium text-stone-700",
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
