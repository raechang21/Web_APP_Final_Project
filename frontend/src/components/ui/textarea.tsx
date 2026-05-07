import type { TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Textarea({
  className,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "w-full rounded-3xl border border-stone-200 bg-white px-4 py-3 text-sm text-ink outline-none transition placeholder:text-stone-400 focus:border-accent focus:ring-4 focus:ring-sky-100",
        className,
      )}
      {...props}
    />
  );
}
