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
  const isLocked = Boolean(currentMbti);
  const [selected, setSelected] = useState<MbtiType | null>(() => {
    try {
      return currentMbti ?? (sessionStorage.getItem("mbti_selected") as MbtiType | null);
    } catch {
      return currentMbti;
    }
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (hydrated && !userName) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit() {
    if (isLocked) {
      navigate("/bigfive");
      return;
    }
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
        title="MBTI"
        description={
          isLocked
            ? "你已經完成 MBTI，這裡只能查看先前選擇，不能再修改。"
            : "MBTI 將人格分為 16 種類型，每種都有獨特的特質組合。選擇最符合你的類型，作為後續測驗的起點。"
        }
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
            <h3 className="font-display text-2xl text-ink sm:text-3xl">
              還不知道你的 MBTI？先到 16Personalities 測一下。
            </h3>
            <p className="text-sm leading-7 text-stone-600 sm:text-base">
              完成 60 題測驗後，回來這頁選擇你的類型。已經知道自己 MBTI 的人可以跳過。
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
                      disabled={isLocked}
                      className={cn(
                        "rounded-[24px] border p-5 text-left transition hover:-translate-y-1 disabled:cursor-not-allowed disabled:hover:translate-y-0",
                        group.tone,
                        active
                          ? "ring-2 ring-ink"
                          : "border-stone-200 bg-white hover:border-stone-300",
                      )}
                      onClick={() => {
                        if (isLocked) {
                          return;
                        }
                        setSelected(item.type);
                        sessionStorage.setItem("mbti_selected", item.type);
                      }}
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
            {submitting ? "儲存中..." : isLocked ? "查看 Big Five" : "前往 Big Five"}
          </Button>
        </div>
      </div>
    </PageShell>
  );
}
