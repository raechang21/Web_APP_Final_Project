import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { fetchDeepAnalysis, streamDeepAnalysis } from "@/api/results";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { useSessionStore } from "@/store/session";

export default function DeepAnalysis() {
  const navigate = useNavigate();
  const hasResults = useSessionStore((state) => state.has_results);
  const patchSession = useSessionStore((state) => state.patchSession);
  const [loading, setLoading] = useState(true);
  const [streaming, setStreaming] = useState(false);
  const [analysis, setAnalysis] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetchDeepAnalysis()
      .then(async (response) => {
        if (!active) {
          return;
        }
        if (response.analysis.comprehensive) {
          setAnalysis(response.analysis.comprehensive);
          patchSession({ has_analysis: true });
          setLoading(false);
          return;
        }
        setStreaming(true);
        setLoading(false);
        await streamDeepAnalysis((event) => {
          if (!active) {
            return;
          }
          if (event.error) {
            setError(event.error);
            setStreaming(false);
            return;
          }
          if (event.chunk) {
            setAnalysis((current) => current + event.chunk);
          }
          if (event.done) {
            patchSession({ has_analysis: true });
            setStreaming(false);
          }
        });
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "綜合分析載入失敗");
          setLoading(false);
          setStreaming(false);
        }
      });
    return () => {
      active = false;
    };
  }, [patchSession]);

  if (!hasResults) {
    return <Navigate to="/results" replace />;
  }

  return (
    <PageShell>
      <SectionHero
        eyebrow="Deep Analysis"
        title="這裡才是 LLM 真正介入的地方。"
        description="這個頁面直接對接後端 SSE，逐段接收模型生成內容。若 session 已經快取過綜合分析，則直接回填，不再重跑一次。"
      />

      <Card className="overflow-hidden">
        <div className="bg-gradient-to-r from-ink to-accent px-6 py-5 text-paper">
          <p className="text-sm uppercase tracking-[0.24em] text-sky-100">SSE Stream</p>
          <h2 className="mt-2 font-display text-4xl">Comprehensive Personality Analysis</h2>
        </div>
        <CardContent className="space-y-5 p-8">
          {loading ? <p className="text-stone-500">正在檢查既有分析...</p> : null}
          {streaming ? (
            <div className="inline-flex items-center rounded-full bg-[rgba(216,164,63,0.2)] px-4 py-2 text-sm text-amber-900">
              AI 正在生成中...
            </div>
          ) : null}
          {error ? <p className="text-sm text-red-500">{error}</p> : null}
          <article className="whitespace-pre-wrap text-base leading-9 text-stone-700">
            {analysis || "尚未生成內容。"}
          </article>
        </CardContent>
      </Card>
    </PageShell>
  );
}
