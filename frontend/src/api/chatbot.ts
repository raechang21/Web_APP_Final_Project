import type {
  ConversationHistoryResponse,
  ConversationSummary,
} from "@/types";

import { apiRequest, streamSse } from "./client";

export function streamChat(
  message: string,
  conversationId: number | null,
  onEvent: (event: {
    chunk?: string;
    done?: boolean;
    error?: string;
    error_code?: string;
    message?: string;
    conversation_id?: number | null;
  }) => void,
) {
  return streamSse("/api/chatbot/stream", {
    method: "POST",
    body: { message, conversation_id: conversationId },
  }, onEvent);
}

export function fetchChatHistory(conversationId?: number | null) {
  const path =
    conversationId == null
      ? "/api/chatbot/history"
      : `/api/chatbot/history/conversation/${conversationId}`;
  return apiRequest<ConversationHistoryResponse>(path);
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


export function deleteHistory(id: number) {
  return apiRequest<{ success: boolean }>(`/api/chatbot/history/${id}`, {
    method: "DELETE",
  });
}

export function deleteAllHistories() {
  return apiRequest<{ success: boolean; deleted: number }>(
    "/api/chatbot/history/all",
    { method: "DELETE" },
  );
}
