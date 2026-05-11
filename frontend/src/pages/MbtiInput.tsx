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
        actions={
          <a
            className="rounded-2xl bg-white px-4 py-3 text-sm text-ink shadow-soft ring-1 ring-stone-200 transition hover:-translate-y-0.5"
            href="https://www.16personalities.com/tw/%E6%80%A7%E6%A0%BC%E6%B8%AC%E8%A9%A6"
            rel="noreferrer"
            target="_blank"
          >
            外部 MBTI 測驗 ↗
          </a>
        }
      />

      <div className="grid gap-6">
        {MBTI_GROUPS.map((group) => (
          <Card key={group.title}>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-stone-400">
                    {group.title}
                  </p>
                  <h2 className="mt-2 font-display text-3xl text-ink">
                    {group.title} 群組
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
                      <div className="text-3xl">{item.icon}</div>
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
