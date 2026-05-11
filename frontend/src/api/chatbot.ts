import type { ChatMessage, ConversationSummary } from "@/types";

import { apiRequest, streamSse } from "./client";

export function streamChat(
  message: string,
  onEvent: (event: { chunk?: string; done?: boolean; error?: string }) => void,
) {
  return streamSse("/api/chatbot/stream", {
    method: "POST",
    body: { message },
  }, onEvent);
}

export function fetchChatHistory() {
  return apiRequest<{ messages: ChatMessage[] }>("/api/chatbot/history");
}

export function fetchAllHistories() {
  return apiRequest<{ user_name?: string; histories: ConversationSummary[] }>(
    "/api/chatbot/history/all",
  );
}

export function clearChatHistory() {
  return apiRequest<{ success: boolean }>("/api/chatbot/clear", {
    method: "POST",
  });
}

export function saveChatHistory() {
  return apiRequest<{ success: boolean; message: string }>("/api/chatbot/save", {
    method: "POST",
  });
}
