import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { quickLogin, startSession } from "@/api/session";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { useSessionStore } from "@/store/session";
import { cn } from "@/lib/utils";

const cards = [
  {
    icon: "🎯",
    title: "MBTI",
    summary: "輸入你的 MBTI\n或前往測驗網站",
    detail: "輸入你的 MBTI，或前往測驗網站完成簡單測驗，快速了解自己在人際互動、思考方式、決策習慣與生活偏好上的傾向，幫助你更清楚認識自己的性格輪廓。",
  },
  {
    icon: "📊",
    title: "五大人格",
    summary: "15 個問題\n快速了解真實的你！",
    detail: "透過 15 個簡短題目，從開放性、盡責性、外向性、親和性與情緒穩定性五個面向分析你的性格特質，幫助你更全面理解自己的行為模式與內在傾向。",
  },
  {
    icon: "⭐",
    title: "星座選擇",
    summary: "你是哪個星座?\n點一下就知道!",
    detail: "選擇你的星座，探索星座性格中常見的特質描述，看看你在人際關係、情緒表達與生活態度上是否符合星座印象，作為輕鬆有趣的自我觀察入口。",
  },
  {
    icon: "🪞",
    title: "黑暗三角",
    summary: "19 題策略思維\n與行為風格評估",
    detail: "透過 19 題測驗，評估你在策略思維、競爭傾向、自我表現與人際判斷上的風格。此測驗並非診斷，而是協助你理解自己在特定情境下可能展現的行為傾向。",
  },
  {
    icon: "🧠",
    title: "結果分析",
    summary: "獲得完整的\n人格分析報告",
    detail: "系統會整合你的 MBTI、Big Five、星座與黑暗三角測驗結果，產出完整的人格分析報告，幫助你從不同角度看見自己的性格特質、優勢與可能需要留意的面向。",
  },
  {
    icon: "💬",
    title: "諮詢助手",
    summary: "AI 諮詢助手解答\n人格相關問題",
    detail: "有任何人格測驗相關問題，都可以詢問 AI 諮詢助手。無論是想理解測驗結果、比較不同人格類型，或進一步探索自己的性格特質，都能獲得即時且清楚的回覆。",
  },
];

export default function Welcome() {
  const navigate = useNavigate();
  const hydrate = useSessionStore((state) => state.hydrate);
  const clear = useSessionStore((state) => state.clear);
  const session = useSessionStore((state) => state);

  const [name, setName] = useState(session.user_name ?? "");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<"new" | "returning" | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  async function handleStart() {
    setError(null);
    setLoading("new");
    try {
      const value = name.trim();
      if (!value) {
        throw new Error("請先輸入你的名字");
      }
      clear();
      const response = await startSession(value);
      await hydrate();
      navigate(response.redirect);
    } catch (err) {
      setError(err instanceof Error ? err.message : "初始化 session 失敗");
    } finally {
      setLoading(null);
    }
  }

  async function handleQuickLogin() {
    setError(null);
    setLoading("returning");
    try {
      const value = name.trim();
      if (!value) {
        throw new Error("請輸入曾經測驗過的名字");
      }
      await quickLogin(value);
      await hydrate();
      navigate("/chatbot");
    } catch (err) {
      setError(err instanceof Error ? err.message : "快速登入失敗");
    } finally {
      setLoading(null);
    }
  }

  return (
    <PageShell>
      <SectionHero
        eyebrow="歡迎"
        title="從多元人格測驗到諮詢小助手＜(´⌯ ̫⌯`)＞"
        description="本系統結合坊間廣為流傳之人格評估工具，輔以具信效度之人格心理測驗：MBTI、五大人格、星座、黑暗三角，進行 AI 綜合分析，打破單一測驗視角的限制，提供多面向的人格詮釋方式。"
      />

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        {expanded === null ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {cards.map((card, i) => (
              <Card
                key={card.title}
                onClick={() => setExpanded(i)}
                className="group cursor-pointer overflow-hidden transition-all duration-300 ease-out hover:-translate-y-1 hover:border-stone-300/80 hover:shadow-[0_24px_70px_rgba(54,47,31,0.14)]"
              >
                <CardContent>
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-stone-100 text-2xl transition-transform duration-300 ease-out group-hover:scale-110 group-hover:rotate-3">
                    {card.icon}
                  </div>
                  <h3 className="mt-4 font-display text-3xl text-ink">{card.title}</h3>
                  <p className="mt-2 whitespace-pre-line text-sm leading-7 text-stone-600">{card.summary}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            <Card key={expanded} className="relative animate-expand-in">
              <CardContent className="space-y-6 p-8 sm:p-10">
                <button
                  onClick={() => setExpanded(null)}
                  className="absolute right-5 top-5 flex h-9 w-9 items-center justify-center rounded-full bg-stone-100 text-stone-500 transition hover:bg-stone-200 hover:text-ink"
                  aria-label="收合"
                >
                  ✕
                </button>

                <div className="flex items-center gap-5">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-stone-100 text-4xl">
                    {cards[expanded].icon}
                  </div>
                  <div>
                    <h3 className="mt-1 font-display text-3xl text-ink sm:text-4xl">
                      {cards[expanded].title}
                    </h3>
                  </div>
                </div>

                <p className="max-w-3xl text-base leading-8 text-stone-700 sm:text-lg sm:leading-9">
                  {cards[expanded].detail}
                </p>
              </CardContent>
            </Card>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
              {cards.map((card, i) => {
                if (i === expanded) return null;
                return (
                  <Card
                    key={card.title}
                    onClick={() => setExpanded(i)}
                    className="group cursor-pointer transition-all duration-300 ease-out hover:-translate-y-1 hover:border-stone-300/80 hover:shadow-[0_18px_50px_rgba(54,47,31,0.1)]"
                  >
                    <CardContent className="p-4 text-center">
                      <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-stone-100 text-xl transition-transform duration-300 ease-out group-hover:scale-110 group-hover:rotate-3">
                        {card.icon}
                      </div>
                      <p className="mt-2 text-sm font-medium text-ink">{card.title}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        <Card className="self-start">
          <CardContent className="space-y-6">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-stone-400">Session</p>
              <h2 className="mt-2 font-display text-3xl text-ink">開始您的探索之旅</h2>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium text-ink" htmlFor="name">
                請輸入您的使用者名稱
              </label>
              <Input
                id="name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="例如：Keye"
              />
              {error ? <p className="text-sm text-red-500">{error}</p> : null}
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <Button onClick={handleStart} disabled={loading !== null}>
                {loading === "new" ? "建立中..." : "開始"}
              </Button>
              <Button variant="secondary" onClick={handleQuickLogin} disabled={loading !== null}>
                {loading === "returning" ? "登入中..." : "快速登入回到 Chatbot"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>
    </PageShell>
  );
}
