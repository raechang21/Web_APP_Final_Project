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
  const darkTriadScores = useSessionStore((state) => state.dark_triad_scores);
  const darkTriadAnswers = useSessionStore((state) => state.dark_triad_answers);
  const profileLocked = useSessionStore((state) => state.profile_locked);
  const patchSession = useSessionStore((state) => state.patchSession);
  const hasDarkTriadRecord = Boolean(darkTriadScores || darkTriadAnswers);

  if (!zodiac) {
    return <Navigate to="/zodiac" replace />;
  }

  async function handleSkip() {
    await skipDarkTriad();
    sessionStorage.removeItem("dark_triad_answers");
    patchSession({
      dark_triad_scores: null,
      dark_triad_answers: null,
      has_results: true,
      profile_locked: true,
    });
    navigate("/results");
  }

  return (
    <PageShell>
      <FlowSteps />
      <SectionHero
        eyebrow="Step 04"
        title="黑暗三角"
        description="黑暗三角是心理學中用來描述三種人格特質概念，本測驗題目參考張益慈、詹雨臻、陳學志（2021）。"
      />

      <Card>
        <CardContent className="space-y-5">
          <h2 className="font-display text-3xl text-ink">什麼是黑暗三角?</h2>
          <p className="text-sm leading-8 text-stone-600">
            聚焦於三種常被誤解的人格傾向：策略性、自我關注，以及規範與衝動控制。理解這些維度，有助於辨識自己在壓力、競爭與人際互動中的反應習慣。
          </p>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-3xl bg-[rgba(157,132,210,0.10)] p-5">
              <h3 className="font-medium text-ink">馬基維利主義</h3>
              <p className="mt-2 text-sm leading-7 text-stone-600">在人際中如何運用策略、掌握情勢，並看待利益與手段。</p>
            </div>
            <div className="rounded-3xl bg-[rgba(215,105,83,0.10)] p-5">
              <h3 className="font-medium text-ink">自戀</h3>
              <p className="mt-2 text-sm leading-7 text-stone-600">如何看待自己的重要性、獨特性、對肯定與關注的需求。</p>
            </div>
            <div className="rounded-3xl bg-stone-200/70 p-5">
              <h3 className="font-medium text-ink">病態人格</h3>
              <p className="mt-2 text-sm leading-7 text-stone-600">在衝動、規範、風險與人際衝突上的反應傾向。</p>
            </div>
          </div>
          <div className="flex flex-wrap justify-end gap-3">
            {profileLocked && !hasDarkTriadRecord ? (
              <Button onClick={() => navigate("/results")}>查看 Results</Button>
            ) : (
              <>
                <Button variant="secondary" onClick={handleSkip} disabled={profileLocked}>
                  跳過直接看結果
                </Button>
                <Button onClick={() => navigate("/dark-triad")}>
                  {hasDarkTriadRecord ? "查看作答" : "開始測驗"}
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </PageShell>
  );
}
