import { useEffect, useRef, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  deleteAllHistories,
  deleteHistory,
  fetchAllHistories,
  fetchChatHistory,
  streamChat,
} from "@/api/chatbot";
import { MessageList } from "@/components/chatbot/MessageList";
import { QuickQuestions } from "@/components/chatbot/QuickQuestions";
import { SidebarSummary } from "@/components/chatbot/SidebarSummary";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import newChatIcon from "@/assets/icons/new-chat.svg";
import { CHATBOT_PROMPTS } from "@/lib/personality";
import { cn, formatDate } from "@/lib/utils";
import { useSessionStore } from "@/store/session";
import type {
  ChatMessage,
  ConversationHistoryResponse,
  ConversationSummary,
} from "@/types";

function seedWelcomeMessage(welcomeMessage: string | null): ChatMessage[] {
  if (!welcomeMessage) {
    return [];
  }
  return [
    {
      role: "assistant",
      content: welcomeMessage,
    },
  ];
}

export default function Chatbot() {
  const session = useSessionStore((state) => state);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [histories, setHistories] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([fetchChatHistory(), fetchAllHistories()])
      .then(([historyResponse, allResponse]) => {
        if (!active) {
          return;
        }
        const seeded =
          historyResponse.messages.length === 0 && historyResponse.conversation_id == null
            ? seedWelcomeMessage(session.welcome_message)
            : historyResponse.messages;
        setMessages(seeded);
        setActiveConversationId(historyResponse.conversation_id);
        setHistories(allResponse.histories);
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "聊天記錄載入失敗");
        }
      });
    return () => {
      active = false;
    };
  }, [session.welcome_message]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (!session.has_results && !session.is_quick_login) {
    return <Navigate to="/" replace />;
  }

  async function refreshHistories() {
    const response = await fetchAllHistories();
    setHistories(response.histories);
    return response.histories;
  }

  function applyHistoryResponse(historyResponse: ConversationHistoryResponse) {
    const nextMessages =
      historyResponse.messages.length === 0 && historyResponse.conversation_id == null
        ? seedWelcomeMessage(session.welcome_message)
        : historyResponse.messages;
    setMessages(nextMessages);
    setActiveConversationId(historyResponse.conversation_id);
  }

  async function handleSelectHistory(conversationId: number) {
    if (streaming) {
      return;
    }
    try {
      setError(null);
      const response = await fetchChatHistory(conversationId);
      applyHistoryResponse(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "聊天記錄載入失敗");
    }
  }

  function handleNewConversation() {
    if (streaming) {
      return;
    }
    setError(null);
    setInput("");
    setMessages([]);
    setActiveConversationId(null);
  }

  async function handleSend(prefilled?: string) {
    const text = (prefilled ?? input).trim();
    if (!text || streaming) {
      return;
    }

    const currentConversationId = activeConversationId;
    const userMessage: ChatMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    const assistantMessage: ChatMessage = { role: "assistant", content: "" };

    setError(null);
    setStreaming(true);
    setInput("");
    setMessages((current) => [...current, userMessage, assistantMessage]);

    try {
      await streamChat(text, currentConversationId, (event) => {
        if (event.conversation_id !== undefined) {
          setActiveConversationId(event.conversation_id ?? null);
        }
        if (event.error_code) {
          const fallbackMessage = event.message ?? "AI 服務暫時無法回應，請稍後再試。";

          setMessages((current) => {
            const copy = [...current];
            const last = copy[copy.length - 1];
            if (last?.role === "assistant") {
              copy[copy.length - 1] = {
                ...last,
                content: fallbackMessage,
              };
            }
            return copy;
          });

          setStreaming(false);
          void refreshHistories();
          return;
        }
        if (event.error) {
          setError(event.error);
          setStreaming(false);
          return;
        }
        if (event.chunk) {
          setMessages((current) => {
            const copy = [...current];
            const last = copy[copy.length - 1];
            if (last?.role === "assistant") {
              copy[copy.length - 1] = {
                ...last,
                content: last.content + event.chunk,
              };
            }
            return copy;
          });
        }
        if (event.done) {
          setStreaming(false);
          void refreshHistories();
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "SSE 連線失敗");
      setStreaming(false);
    }
  }

  async function handleDeleteHistory(conversationId: number) {
    if (!confirm("確定刪除這筆對話記錄嗎？")) {
      return;
    }

    const deletingActiveConversation = conversationId === activeConversationId;

    try {
      setError(null);
      await deleteHistory(conversationId);
      const remainingHistories = await refreshHistories();

      if (!deletingActiveConversation) {
        return;
      }

      const nextConversation = remainingHistories[0];
      if (nextConversation) {
        const response = await fetchChatHistory(nextConversation.id);
        applyHistoryResponse(response);
      } else {
        applyHistoryResponse({ conversation_id: null, messages: [] });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "刪除失敗");
    }
  }

  async function handleClearAllHistories() {
    if (!confirm(`確定要清除全部 ${histories.length} 筆對話記錄嗎？\n此動作無法復原。`)) {
      return;
    }
    try {
      setError(null);
      await deleteAllHistories();
      setHistories([]);
      applyHistoryResponse({ conversation_id: null, messages: [] });
    } catch (err) {
      setError(err instanceof Error ? err.message : "清除失敗");
    }
  }

  return (
    <PageShell className="space-y-8">
      <SectionHero
        eyebrow="AI Chatbot"
        description=""
        title="諮詢小助手＜(´⌯ ̫⌯`)＞"
      />

      <div className="grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)_280px]">
        <SidebarSummary session={session} />

        <Card className="h-[90vh]">
          <CardContent className="flex h-full flex-col gap-4 p-0">
            <div className="border-b border-stone-200 px-6 py-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="font-display text-3xl text-ink">聊天室</h2>
                </div>
                <button
                  type="button"
                  onClick={handleNewConversation}
                  disabled={streaming}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-xl transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-50"
                  aria-label="新增對話"
                  title="新增對話"
                >
                  <img
                    src={newChatIcon}
                    alt=""
                    aria-hidden="true"
                    className="object-contain opacity-80"
                    style={{ height: "20px", width: "20px" }}
                  />
                </button>
              </div>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto px-6 py-5">
              {error ? <p className="text-sm text-red-500">{error}</p> : null}
              <MessageList messages={messages} />
              <div ref={bottomRef} />
            </div>

            <div className="border-t border-stone-200 px-6 py-5">
              <div className="space-y-3">
                <Textarea
                  rows={4}
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      void handleSend();
                    }
                  }}
                  placeholder="直接問：我的性格在關係裡常怎麼反應？"
                />
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={() => void handleSend()}
                    disabled={streaming || !input.trim()}
                    className="inline-flex items-center justify-center rounded-2xl bg-ink px-4 py-3 text-sm font-medium text-paper transition hover:-translate-y-0.5 hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {streaming ? "串流中..." : "送出"}
                  </button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-4">
              <h3 className="font-display text-2xl text-ink">快速問題</h3>
              <QuickQuestions prompts={CHATBOT_PROMPTS} onSelect={(prompt) => void handleSend(prompt)} />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-display text-2xl text-ink">對話紀錄</h3>
                {histories.length > 0 ? (
                  <button
                    type="button"
                    onClick={() => void handleClearAllHistories()}
                    disabled={streaming}
                    className="flex items-center gap-1 rounded-full px-3 py-1.5 text-xs text-stone-500 transition hover:bg-red-50 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50"
                    aria-label="清除全部記錄"
                  >
                    <span>全部清除</span>
                  </button>
                ) : null}
              </div>
              <div className="max-h-[400px] space-y-3 overflow-y-auto pr-1">
                {histories.length === 0 ? (
                  <p className="text-sm text-stone-500">目前沒有保存過的對話。</p>
                ) : (
                  histories.map((history) => {
                    const active = history.id === activeConversationId;

                    return (
                      <div key={history.id} className="group relative">
                        <button
                          type="button"
                          onClick={() => void handleSelectHistory(history.id)}
                          disabled={streaming}
                          className={cn(
                            "w-full rounded-2xl p-4 pr-14 text-left transition-all duration-300",
                            active
                              ? "bg-stone-100 ring-1 ring-stone-300"
                              : "bg-stone-50 hover:bg-stone-100",
                            streaming && "cursor-not-allowed opacity-60",
                          )}
                        >
                          <p className="text-sm font-medium text-ink">
                            {history.preview || "空白對話"}
                          </p>
                          <p className="mt-1 text-xs text-stone-500">
                            {formatDate(history.timestamp)} · {history.message_count} 則訊息
                          </p>
                        </button>
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            void handleDeleteHistory(history.id);
                          }}
                          disabled={streaming}
                          className="absolute right-3 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full text-stone-400 opacity-0 transition-all duration-300 group-hover:opacity-100 hover:bg-red-50 hover:text-red-500 disabled:cursor-not-allowed disabled:opacity-50"
                          aria-label="刪除這筆對話"
                        >
                          🗑️
                        </button>
                      </div>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageShell>
  );
}
