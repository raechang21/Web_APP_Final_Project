import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { quickLogin, startSession } from "@/api/session";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { useSessionStore } from "@/store/session";

const cards = [
  ["🎯", "MBTI", "先建立你的認知偏好輪廓"],
  ["📊", "Big Five", "用五大人格維度補齊細節"],
  ["⭐", "Zodiac", "把性格敘事拉回日常感受"],
  ["🪞", "Dark Triad", "可選擇性探索策略與自我風格"],
  ["🧠", "Deep Analysis", "整合分析你的呼應與矛盾"],
  ["💬", "Chatbot", "把結果帶進實際對話"],
];

export default function Welcome() {
  const navigate = useNavigate();
  const hydrate = useSessionStore((state) => state.hydrate);
  const session = useSessionStore((state) => state);

  const [name, setName] = useState(session.user_name ?? "");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<"new" | "returning" | null>(null);

  async function handleStart() {
    setError(null);
    setLoading("new");
    try {
      const value = name.trim();
      if (!value) {
        throw new Error("請先輸入你的名字");
      }
      await startSession(value);
      await hydrate();
      navigate("/mbti");
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
        eyebrow="人格旅程"
        title="把原本散落在 Jinja 裡的流程，重組成一條清楚的探索路徑。"
        description="這一版先把核心流程重構成 React SPA：welcome、測驗流程、結果、深度分析，以及 SSE chatbot。後端 session 與 SQLite 記錄則沿用 FastAPI branch。"
      />

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {cards.map(([icon, title, text]) => (
            <Card key={title} className="overflow-hidden">
              <CardContent className="space-y-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-stone-100 text-2xl">
                  {icon}
                </div>
                <div>
                  <h2 className="font-display text-2xl text-ink">{title}</h2>
                  <p className="mt-2 text-sm leading-7 text-stone-600">{text}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="self-start">
          <CardContent className="space-y-6">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-stone-400">Session</p>
              <h2 className="mt-2 font-display text-3xl text-ink">先決定你要怎麼進入</h2>
              <p className="mt-3 text-sm leading-7 text-stone-600">
                新使用者會從 MBTI 開始；舊使用者則可直接從 SQLite memory 回到 chatbot。
              </p>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium text-ink" htmlFor="name">
                名字
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
                {loading === "new" ? "建立中..." : "開始重構後流程"}
              </Button>
              <Button variant="secondary" onClick={handleQuickLogin} disabled={loading !== null}>
                {loading === "returning" ? "登入中..." : "快速登入回到 Chatbot"}
              </Button>
            </div>

            <div className="rounded-3xl bg-stone-50 p-4 text-sm leading-7 text-stone-600">
              如果你只是要驗證前後端串接，也可以直接打開 <code>/diagnostic</code> 頁面塞測試資料。
            </div>
          </CardContent>
        </Card>
      </section>
    </PageShell>
  );
}
