import { useEffect, useMemo, useRef, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  clearChatHistory,
  deleteAllHistories,
  deleteHistory,
  fetchAllHistories,
  fetchChatHistory,
  saveChatHistory,
  streamChat,
} from "@/api/chatbot";
import { MessageList } from "@/components/chatbot/MessageList";
import { QuickQuestions } from "@/components/chatbot/QuickQuestions";
import { SidebarSummary } from "@/components/chatbot/SidebarSummary";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { CHATBOT_PROMPTS } from "@/lib/personality";
import { formatDate } from "@/lib/utils";
import { useSessionStore } from "@/store/session";
import type { ChatMessage, ConversationSummary } from "@/types";

export default function Chatbot() {
  const session = useSessionStore((state) => state);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [histories, setHistories] = useState<ConversationSummary[]>([]);
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
          historyResponse.messages.length === 0 && session.welcome_message
            ? [
                {
                  role: "assistant" as const,
                  content: session.welcome_message,
                },
              ]
            : historyResponse.messages;
        setMessages(seeded);
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

  const promptList = useMemo(() => CHATBOT_PROMPTS, []);

  if (!session.has_results && !session.is_quick_login) {
    return <Navigate to="/" replace />;
  }

  async function handleSend(prefilled?: string) {
    const text = (prefilled ?? input).trim();
    if (!text || streaming) {
      return;
    }

    setError(null);
    setStreaming(true);
    setInput("");

    const userMessage: ChatMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    const assistantMessage: ChatMessage = { role: "assistant", content: "" };

    setMessages((current) => [...current, userMessage, assistantMessage]);

    try {
      await streamChat(text, (event) => {
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
          fetchAllHistories().then((response) => setHistories(response.histories)).catch(() => null);
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "SSE 連線失敗");
      setStreaming(false);
    }
  }

  async function handleClear() {
    await clearChatHistory();
    setMessages([]);
  }

  async function handleSave() {
    await saveChatHistory();
    const response = await fetchAllHistories();
    setHistories(response.histories);
  }

  async function handleDeleteHistory(id: number) {
    if (!confirm("確定刪除這筆對話記錄嗎？")) return;
    try {
      await deleteHistory(id);
      setHistories((current) => current.filter((h) => h.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "刪除失敗");
    }
  }
  
  async function handleClearAllHistories() {
    if (!confirm(`確定要清除全部 ${histories.length} 筆對話記錄嗎？\n此動作無法復原。`)) return;
    try {
      await deleteAllHistories();
      setHistories([]);
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

        <Card className="h-[70vh]">
          <CardContent className="flex h-full flex-col gap-4 p-0">
            <div className="border-b border-stone-200 px-6 py-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="font-display text-3xl text-ink">聊天室</h2>
                </div>
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
                      handleSend();
                    }
                  }}
                  placeholder="直接問：我的性格在關係裡常怎麼反應？"
                />
                <div className="flex justify-end">
                  <Button onClick={() => handleSend()} disabled={streaming || !input.trim()}>
                    {streaming ? "串流中..." : "送出"}
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-4">
              <h3 className="font-display text-2xl text-ink">快速問題</h3>
              <QuickQuestions prompts={promptList} onSelect={(prompt) => handleSend(prompt)} />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-display text-2xl text-ink">對話紀錄</h3>
                {histories.length > 0 ? (
                  <button
                    type="button"
                    onClick={handleClearAllHistories}
                    className="flex items-center gap-1 rounded-full px-3 py-1.5 text-xs text-stone-500 transition hover:bg-red-50 hover:text-red-600"
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
                  histories.map((history) => (
                    <div key={history.id} className="group relative">
                      <div className="rounded-2xl bg-stone-50 p-4 transition-all duration-300 group-hover:bg-stone-100 group-hover:pr-14">
                        <p className="text-sm font-medium text-ink">{history.preview || "空白對話"}</p>
                        <p className="mt-1 text-xs text-stone-500">
                          {formatDate(history.timestamp)} · {history.message_count} 則訊息
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleDeleteHistory(history.id)}
                        className="absolute right-3 top-1/2 flex h-9 w-9 -translate-y-1/2 scale-75 items-center justify-center rounded-full text-stone-400 opacity-0 transition-all duration-300 group-hover:scale-100 group-hover:opacity-100 hover:bg-red-50 hover:text-red-500"
                        aria-label="刪除這筆對話"
                      >
                        刪除
                      </button>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageShell>
  );
}
