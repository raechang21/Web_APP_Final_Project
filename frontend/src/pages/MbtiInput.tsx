import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { submitMbti } from "@/api/tests";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FlowSteps } from "@/components/layout/FlowSteps";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { MBTI_GROUPS } from "@/lib/personality";
import type { MbtiType } from "@/types";
import { useSessionStore } from "@/store/session";
import { cn } from "@/lib/utils";

export default function MbtiInput() {
  const navigate = useNavigate();
  const patchSession = useSessionStore((state) => state.patchSession);
  const hydrated = useSessionStore((state) => state.hydrated);
  const userName = useSessionStore((state) => state.user_name);
  const currentMbti = useSessionStore((state) => state.mbti);
  const [selected, setSelected] = useState<MbtiType | null>(currentMbti);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (hydrated && !userName) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit() {
    if (!selected) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const response = await submitMbti(selected);
      patchSession({ mbti: response.mbti });
      navigate("/bigfive");
    } catch (err) {
      setError(err instanceof Error ? err.message : "MBTI 儲存失敗");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageShell>
      <FlowSteps />
      <SectionHero
        eyebrow="Step 01"
        title="先用 MBTI 定位你的偏好起點。"
        description="這裡先走簡化流程，直接選定類型；之後若要接 16Personalities 外部流程，也可以在這頁延伸。"
      />
      <a href="https://www.16personalities.com/tw/%E6%80%A7%E6%A0%BC%E6%B8%AC%E8%A9%A6"
        rel="noreferrer"
        target="_blank"
        className="group flex items-center justify-between gap-6 rounded-[28px] border border-stone-200/80 bg-gradient-to-br from-white to-stone-50 p-6 shadow-soft transition-all duration-300 ease-out hover:-translate-y-1 hover:border-ink/30 hover:shadow-[0_24px_70px_rgba(54,47,31,0.14)] sm:p-8"
      >
        <div className="flex items-start gap-5">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-ink text-2xl text-white transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3">
            🧭
          </div>
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.24em] text-stone-400">
              Optional · 約 12 分鐘
            </p>
            <h3 className="font-display text-2xl text-ink sm:text-3xl">
              還不知道你的 MBTI？先到 16Personalities 測一下。
            </h3>
            <p className="text-sm leading-7 text-stone-600 sm:text-base">
              在外部完成 60 題測驗後，回來這頁直接選定你的類型即可。已經知道自己 MBTI 的人可以跳過。
            </p>
          </div>
        </div>
        <div className="hidden shrink-0 items-center gap-2 rounded-full bg-ink px-5 py-3 text-sm font-medium text-white transition-transform duration-300 group-hover:translate-x-1 sm:flex">
          前往測驗
          <span className="text-base">↗</span>
        </div>
      </a>
      <div className="grid gap-6">
        {MBTI_GROUPS.map((group) => (
          <Card key={group.title}>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="mt-2 font-display text-3xl text-ink">
                    {group.title} 
                  </h2>
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {group.types.map((item) => {
                  const active = item.type === selected;
                  return (
                    <button
                      key={item.type}
                      className={cn(
                        "rounded-[24px] border p-5 text-left transition hover:-translate-y-1",
                        group.tone,
                        active
                          ? "ring-2 ring-ink"
                          : "border-stone-200 bg-white hover:border-stone-300",
                      )}
                      onClick={() => setSelected(item.type)}
                      type="button"
                    >
                      <div className="flex h-16 w-16 items-center justify-center overflow-hidden">
                        <img
                          src={item.image}
                          alt={`${item.type} ${item.label}`}
                          className="h-full w-full object-contain"
                          loading="lazy"
                        />
                      </div>
                      <div className="mt-4">
                        <p className="font-display text-3xl text-ink">{item.type}</p>
                        <p className="mt-1 text-sm text-stone-600">{item.label}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        ))}

        {error ? <p className="text-sm text-red-500">{error}</p> : null}
        <div className="flex justify-end">
          <Button onClick={handleSubmit} disabled={!selected || submitting}>
            {submitting ? "儲存中..." : "前往 Big Five"}
          </Button>
        </div>
      </div>
    </PageShell>
  );
}
