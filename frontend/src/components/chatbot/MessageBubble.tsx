import type { ChatMessage } from "@/types";

import { cn, formatDate } from "@/lib/utils";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const assistant = message.role === "assistant";

  return (
    <div className={cn("flex gap-3", assistant ? "justify-start" : "justify-end")}>
      {assistant ? (
        <div className="h-10 w-10 shrink-0 overflow-hidden rounded-full">
          <img
            src="/assistant-avatar.png"
            alt="AI 諮詢助手"
            className="h-full w-full object-cover"
          />
        </div>
      ) : null}
      <div
        className={cn(
          "max-w-[80%] rounded-[24px] px-4 py-3 text-sm leading-7 shadow-sm",
          assistant
            ? "rounded-tl-md bg-stone-100 text-ink"
            : "rounded-tr-md bg-accent text-white",
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.timestamp ? (
          <p className={cn("mt-2 text-[11px]", assistant ? "text-stone-400" : "text-sky-100")}>
            {formatDate(message.timestamp)}
          </p>
        ) : null}
      </div>
      {!assistant ? (
       <div className="flex h-10 w-10 items-center justify-center rounded-full bg-coral text-white">
          你
        </div>
      ) : null}
    </div>
  );
}
