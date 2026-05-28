import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  cacheDeepAnalysis,
  fetchDeepAnalysis,
  streamDeepAnalysis,
} from "@/api/results";
import { Card, CardContent } from "@/components/ui/card";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { useSessionStore } from "@/store/session";
import type { DeepAnalysisResponse } from "@/types";

function getAnalysisCacheKey(response: DeepAnalysisResponse) {
  return `pp.deep-analysis:${JSON.stringify({
    mbti: response.mbti,
    bigfive_scores: response.bigfive_scores,
    zodiac: response.zodiac,
    dark_triad_scores: response.dark_triad_scores,
  })}`;
}

function readCachedAnalysis(cacheKey: string) {
  return window.localStorage.getItem(cacheKey) ?? "";
}

function writeCachedAnalysis(cacheKey: string, analysis: string) {
  window.localStorage.setItem(cacheKey, analysis);
}

export default function DeepAnalysis() {
  const hasResults = useSessionStore((state) => state.has_results);
  const patchSession = useSessionStore((state) => state.patchSession);
  const [loading, setLoading] = useState(true);
  const [streaming, setStreaming] = useState(false);
  const [analysis, setAnalysis] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    let analysisBuffer = "";
    fetchDeepAnalysis()
      .then(async (response) => {
        if (!active) {
          return;
        }
        const cacheKey = getAnalysisCacheKey(response);
        const cachedAnalysis =
          response.analysis.comprehensive || readCachedAnalysis(cacheKey);

        if (cachedAnalysis) {
          analysisBuffer = cachedAnalysis;
          setAnalysis(cachedAnalysis);
          writeCachedAnalysis(cacheKey, cachedAnalysis);
          patchSession({ has_analysis: true });
          setLoading(false);
          return;
        }

        setAnalysis("");
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
          if (event.cached && event.analysis) {
            analysisBuffer = event.analysis;
            setAnalysis(event.analysis);
          }
          if (event.chunk) {
            analysisBuffer += event.chunk;
            setAnalysis(analysisBuffer);
          }
          if (event.done) {
            setStreaming(false);
            if (!analysisBuffer.trim()) {
              return;
            }

            writeCachedAnalysis(cacheKey, analysisBuffer);
            patchSession({ has_analysis: true });
            void cacheDeepAnalysis(analysisBuffer).catch((err) => {
              if (active) {
                setError(
                  err instanceof Error ? err.message : "分析快取保存失敗",
                );
              }
            });
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
        title="AI綜合性格分析"
        description=" "
      />

      <Card className="overflow-hidden">
        <div className="bg-gradient-to-r from-ink to-accent px-6 py-5 text-paper">
          <h2 className="mt-2 font-display text-4xl"> Personality Analysis</h2>
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
