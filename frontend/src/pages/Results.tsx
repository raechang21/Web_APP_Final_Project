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
        eyebrow="結果"
        title="資料總覽"
        description="MBTI、五大人格、星座與黑暗三角測驗結果一覽"
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
                <p className="text-sm text-stone-500">星座</p>
                <h2 className="mt-2 font-display text-4xl text-ink">
                  {ZODIAC_META[data.zodiac]?.icon} {data.zodiac}
                </h2>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <p className="text-sm text-stone-500">黑暗三角</p>
                <h2 className="mt-2 font-display text-3xl text-ink">
                  {data.dark_triad_scores ? "已完成" : "已跳過"}
                </h2>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-[1fr_0.95fr]">
            <Card>
              <CardContent className="space-y-6">
                <h2 className="font-display text-3xl text-ink">五大人格分析</h2>
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
                <div className="space-y-3 border-t border-stone-200 pt-6">
                  <h3 className="font-display text-2xl text-ink">解讀</h3>
                  <p className="whitespace-pre-wrap text-sm leading-8 text-stone-600">
                    {data.analysis.bigfive ?? "尚未取得 Big Five 靜態模板"}
                  </p>
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
                  <h2 className="font-display text-3xl text-ink">星座分析</h2>
                  <p className="text-sm leading-8 text-stone-600">
                    {data.analysis.zodiac?.description ?? "尚未取得星座模板"}
                  </p>
                </CardContent>
              </Card>

              {data.dark_triad_scores ? (
                <Card>
                  <CardContent className="space-y-4">
                    <h2 className="font-display text-3xl text-ink">黑暗三角分析</h2>
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

              <Card>
                <CardContent className="space-y-4">
                  <h2 className="font-display text-2xl text-ink">
                    💡 最後，我們想告訴你的是……
                  </h2>
                  <p className="text-sm leading-8 text-stone-600">
                    人格測驗只是一面鏡子，幫助你更了解自己的一個工具。它不是標籤,更不是限制。
                  </p>
                  <p className="text-sm leading-8 text-stone-600">
                    你是獨一無二的個體,遠比任何測驗結果更加豐富和複雜。這些分析只是捕捉了你在某個時刻的狀態,而真正的你會隨著經驗、環境和選擇而持續成長與改變。
                  </p>
                  <p className="text-sm leading-8 text-stone-600">
                    請記住:人格是流動的光譜,而非固定的標籤。你永遠有能力突破框架,創造屬於自己的道路。
                  </p>

                  <div className="space-y-3 border-t border-stone-200 pt-4">
                    <h3 className="font-display text-xl text-ink">⚠️ 重要提醒</h3>
                    <ul className="space-y-2 text-sm leading-7 text-stone-600">
                      <li>
                        ⚠️ <strong className="text-ink">測驗結果僅供參考</strong>──這些工具基於心理學理論,但不是專業診斷。
                      </li>
                      <li>
                        ⚠️ <strong className="text-ink">避免過度標籤化</strong>──不要讓測驗結果成為自我設限的理由,你的潛能遠超過任何分類。
                      </li>
                      <li>
                        ⚠️ <strong className="text-ink">人格會改變</strong>──隨著年齡、經驗和環境的變化,你的特質也可能隨之調整。
                      </li>
                      <li>
                        ⚠️ <strong className="text-ink">接納多元性</strong>──每種人格類型都有其優勢,沒有絕對的好壞之分。
                      </li>
                      <li>
                        ⚠️ <strong className="text-ink">尋求專業協助</strong>──如果在自我探索過程中遇到困擾,建議尋求專業心理諮商師的幫助。
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <div className="flex flex-wrap justify-end gap-3">
            <Button variant="secondary" onClick={handleRestart}>
              重新測驗
            </Button>
            <Button variant="accent" onClick={() => navigate("/deep-analysis")}>
              進入 Deep Analysis
            </Button>
            <Button variant="accent" onClick={() => navigate("/chatbot")}>
              打開 Chatbot
            </Button>
          </div>
        </div>
      ) : null}
    </PageShell>
  );
}
