import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { fetchBigFiveChart, fetchResults } from "@/api/results";
import { restartSession } from "@/api/session";
import { BigFiveRadar } from "@/components/charts/BigFiveRadar";
import { ScoreBar } from "@/components/charts/ScoreBar";
import { FlowSteps } from "@/components/layout/FlowSteps";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { BIG_FIVE_META, DARK_TRIAD_META, ZODIAC_META } from "@/lib/personality";
import { useSessionStore } from "@/store/session";
import type { PlotlyFigure, ResultsResponse } from "@/types";

export default function Results() {
  const navigate = useNavigate();
  const hasResults = useSessionStore((state) => state.has_results);
  const zodiac = useSessionStore((state) => state.zodiac);
  const setSession = useSessionStore((state) => state.setSession);
  const clear = useSessionStore((state) => state.clear);
  const [data, setData] = useState<ResultsResponse | null>(null);
  const [chart, setChart] = useState<PlotlyFigure | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([fetchResults(), fetchBigFiveChart()])
      .then(([results, figure]) => {
        if (!active) {
          return;
        }
        setData(results);
        setChart(figure);
        setSession({
          user_name: useSessionStore.getState().user_name,
          mbti: results.mbti,
          bigfive_scores: results.bigfive_scores,
          zodiac: results.zodiac,
          dark_triad_scores: results.dark_triad_scores,
          has_results: true,
          has_analysis: Boolean(results.analysis.comprehensive),
          is_quick_login: useSessionStore.getState().is_quick_login,
          welcome_message: useSessionStore.getState().welcome_message,
        });
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "結果載入失敗");
        }
      });

    return () => {
      active = false;
    };
  }, [setSession]);

  if (!hasResults && zodiac) {
    return <Navigate to="/dark-triad-intro" replace />;
  }

  if (!hasResults && !zodiac) {
    return <Navigate to="/mbti" replace />;
  }

  async function handleRestart() {
    await restartSession();
    clear();
    navigate("/");
  }

  return (
    <PageShell>
      <FlowSteps />
      <SectionHero
        eyebrow="Results"
        title="這一頁先把資料整合成可讀的總覽，而不是急著堆更多動畫。"
        description="MBTI、Big Five、Zodiac 與可選的 Dark Triad 現在都能透過 FastAPI JSON 直接餵進 React，這是整個前後端分離重構的關鍵交界。"
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/deep-analysis")}>
              查看綜合分析
            </Button>
            <Button variant="accent" onClick={() => navigate("/chatbot")}>
              打開 Chatbot
            </Button>
          </>
        }
      />

      {error ? <p className="text-sm text-red-500">{error}</p> : null}
      {!data ? <p className="text-stone-500">結果載入中...</p> : null}

      {data ? (
        <div className="grid gap-6">
          <div className="grid gap-4 lg:grid-cols-3">
            <Card>
              <CardContent>
                <p className="text-sm text-stone-500">MBTI</p>
                <h2 className="mt-2 font-display text-4xl text-ink">{data.mbti}</h2>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <p className="text-sm text-stone-500">Zodiac</p>
                <h2 className="mt-2 font-display text-4xl text-ink">
                  {ZODIAC_META[data.zodiac]?.icon} {data.zodiac}
                </h2>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <p className="text-sm text-stone-500">Dark Triad</p>
                <h2 className="mt-2 font-display text-3xl text-ink">
                  {data.dark_triad_scores ? "已完成" : "已跳過"}
                </h2>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 xl:grid-cols-[1fr_0.95fr]">
            <Card>
              <CardContent className="space-y-6">
                <h2 className="font-display text-3xl text-ink">Big Five Radar</h2>
                {chart ? <BigFiveRadar figure={chart} /> : null}
                <div className="space-y-4">
                  {BIG_FIVE_META.map(({ key, label, color }) => (
                    <ScoreBar
                      key={key}
                      label={label}
                      score={data.bigfive_scores[key]}
                      indicatorClassName={color}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="space-y-6">
              <Card>
                <CardContent className="space-y-4">
                  <h2 className="font-display text-3xl text-ink">MBTI 分析</h2>
                  <p className="text-sm leading-8 text-stone-600">
                    {data.analysis.mbti?.description ?? "尚未取得 MBTI 靜態模板"}
                  </p>
                  {data.analysis.mbti?.strengths?.length ? (
                    <ul className="space-y-2 text-sm text-stone-600">
                      {data.analysis.mbti.strengths.map((item) => (
                        <li key={item}>• {item}</li>
                      ))}
                    </ul>
                  ) : null}
                </CardContent>
              </Card>

              <Card>
                <CardContent className="space-y-4">
                  <h2 className="font-display text-3xl text-ink">Big Five 解讀</h2>
                  <p className="whitespace-pre-wrap text-sm leading-8 text-stone-600">
                    {data.analysis.bigfive ?? "尚未取得 Big Five 靜態模板"}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="space-y-4">
                  <h2 className="font-display text-3xl text-ink">Zodiac 視角</h2>
                  <p className="text-sm leading-8 text-stone-600">
                    {data.analysis.zodiac?.description ?? "尚未取得星座模板"}
                  </p>
                </CardContent>
              </Card>

              {data.dark_triad_scores ? (
                <Card>
                  <CardContent className="space-y-4">
                    <h2 className="font-display text-3xl text-ink">Dark Triad 詳細</h2>
                    {DARK_TRIAD_META.map(({ key, label, color }) => (
                      <ScoreBar
                        key={key}
                        label={label}
                        score={data.dark_triad_scores![key]}
                        indicatorClassName={color}
                      />
                    ))}
                    {data.analysis.dark_triad ? (
                      <p className="whitespace-pre-wrap text-sm leading-8 text-stone-600">
                        {data.analysis.dark_triad}
                      </p>
                    ) : null}
                  </CardContent>
                </Card>
              ) : null}
            </div>
          </div>

          <div className="flex flex-wrap justify-end gap-3">
            <Button variant="secondary" onClick={handleRestart}>
              重新測驗
            </Button>
            <Button variant="accent" onClick={() => navigate("/deep-analysis")}>
              進入 Deep Analysis
            </Button>
          </div>
        </div>
      ) : null}
    </PageShell>
  );
}
