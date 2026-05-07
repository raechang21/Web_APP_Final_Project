import type { ChatMessage } from "@/types";

import { MessageBubble } from "./MessageBubble";

export function MessageList({ messages }: { messages: ChatMessage[] }) {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <MessageBubble
          key={`${message.role}-${index}-${message.timestamp ?? ""}`}
          message={message}
        />
      ))}
    </div>
  );
}
