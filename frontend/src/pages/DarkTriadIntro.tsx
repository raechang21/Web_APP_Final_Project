import { Navigate, useNavigate } from "react-router-dom";

import { skipDarkTriad } from "@/api/tests";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FlowSteps } from "@/components/layout/FlowSteps";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { useSessionStore } from "@/store/session";

export default function DarkTriadIntro() {
  const navigate = useNavigate();
  const zodiac = useSessionStore((state) => state.zodiac);
  const patchSession = useSessionStore((state) => state.patchSession);

  if (!zodiac) {
    return <Navigate to="/zodiac" replace />;
  }

  async function handleSkip() {
    await skipDarkTriad();
    patchSession({ dark_triad_scores: null, has_results: true });
    navigate("/results");
  }

  return (
    <PageShell>
      <FlowSteps />
      <SectionHero
        eyebrow="Step 04"
        title="黑暗三角保留為選做，因為它應該是擴充，不該是阻礙。"
        description="這部分更接近策略傾向與自我呈現風格，不適合作為單一標籤。你可以做，也可以跳過，整體流程都能繼續。"
      />

      <Card>
        <CardContent className="space-y-5">
          <h2 className="font-display text-3xl text-ink">什麼是 Dark Triad</h2>
          <p className="text-sm leading-8 text-stone-600">
            它聚焦於三種常被誤解的人格傾向：策略性、自我展示，以及規則邊界感。適度理解這些維度，有助於你辨識自己在壓力、競爭與人際操作中的習慣。
          </p>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-3xl bg-[rgba(157,132,210,0.10)] p-5">
              <h3 className="font-medium text-ink">馬基維利主義</h3>
              <p className="mt-2 text-sm leading-7 text-stone-600">你如何看待手段、布局與情勢掌控。</p>
            </div>
            <div className="rounded-3xl bg-[rgba(215,105,83,0.10)] p-5">
              <h3 className="font-medium text-ink">自戀</h3>
              <p className="mt-2 text-sm leading-7 text-stone-600">你如何處理自信、舞台感與自我價值。</p>
            </div>
            <div className="rounded-3xl bg-stone-200/70 p-5">
              <h3 className="font-medium text-ink">精神病態</h3>
              <p className="mt-2 text-sm leading-7 text-stone-600">你在衝突、規範與刺激追求上的邊界感。</p>
            </div>
          </div>
          <div className="flex flex-wrap justify-end gap-3">
            <Button variant="secondary" onClick={handleSkip}>
              跳過直接看結果
            </Button>
            <Button onClick={() => navigate("/dark-triad")}>開始測驗</Button>
          </div>
        </CardContent>
      </Card>
    </PageShell>
  );
}
