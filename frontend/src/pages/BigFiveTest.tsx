import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { fetchBigFiveQuestions, submitBigFive } from "@/api/tests";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FlowSteps } from "@/components/layout/FlowSteps";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { BIG_FIVE_OPTIONS } from "@/lib/personality";
import { cn } from "@/lib/utils";
import { useSessionStore } from "@/store/session";
import type { BigFiveQuestion } from "@/types";

export default function BigFiveTest() {
  const navigate = useNavigate();
  const patchSession = useSessionStore((state) => state.patchSession);
  const mbti = useSessionStore((state) => state.mbti);
  const [questions, setQuestions] = useState<BigFiveQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, number>>(() => {
    try {
      const saved = sessionStorage.getItem("bigfive_answers");
      return saved ? (JSON.parse(saved) as Record<number, number>) : {};
    } catch {
      return {};
    }
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    fetchBigFiveQuestions()
      .then((response) => {
        if (active) {
          setQuestions(response.questions);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "載入 Big Five 題目失敗");
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  if (!mbti) {
    return <Navigate to="/mbti" replace />;
  }

  const completed = Object.keys(answers).length;

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    try {
      const response = await submitBigFive(answers);
      patchSession({
        bigfive_scores: response.bigfive_scores,
        has_results: false,
      });
      navigate("/zodiac");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Big Five 提交失敗");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageShell>
      <FlowSteps />
      <SectionHero
        eyebrow="Step 02"
        title="Big Five"
        description="這個測驗幫助你了解你的五大人格特質：開放性、嚴謹性、外向性、友善性、神經質（李仁豪、鍾芯瑜，2020）。每題請選擇最符合你的反應，幫助我們更全面地分析你的性格特質。這些都是人格的自然組成部分！放輕鬆，跟著直覺選就對了😊😊。"
      />


      {loading ? <p className="text-stone-500">題目載入中...</p> : null}
      {error ? <p className="text-sm text-red-500">{error}</p> : null}

      <div className="space-y-4">
        {questions.map((question, index) => (
          <Card key={question.id}>
            <CardContent className="space-y-5">
              <div className="flex gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-coral text-white">
                  {index + 1}
                </div>
                <div>
                  <p className="text-lg font-medium text-ink">{question.text}</p>
                </div>
              </div>
              <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
                {BIG_FIVE_OPTIONS.map((option) => {
                  const active = answers[question.id] === option.value;
                  return (
                    <button
                      key={option.value}
                      type="button"
                      className={cn(
                        "rounded-2xl border px-4 py-4 text-center transition hover:-translate-y-0.5",
                        active
                          ? "border-accent bg-accent text-white"
                          : "border-stone-200 bg-white text-stone-600 hover:border-stone-300",
                      )}
                      onClick={() =>
                        setAnswers((current) => {
                          const next = { ...current, [question.id]: option.value };
                          sessionStorage.setItem("bigfive_answers", JSON.stringify(next));
                          return next;
                        })
                      }
                    >
                      <div className="text-2xl">{option.emoji}</div>
                      <p className="mt-2 text-sm">{option.label}</p>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="h-20 sm:h-24" aria-hidden />
      <div className="pointer-events-none fixed inset-x-0 bottom-0 z-20 px-4 pb-4 sm:px-6 sm:pb-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="pointer-events-auto grid grid-cols-[1fr_auto_1fr] items-center gap-4 rounded-[28px] border border-stone-200/80 bg-[rgba(255,253,250,0.92)] px-6 py-4 shadow-[0_18px_60px_rgba(54,47,31,0.12)] backdrop-blur">
            <div aria-hidden />
            <div className="text-center">
              <p className="text-xs uppercase tracking-[0.24em] text-stone-400">作答進度</p>
              <p className="font-display text-2xl text-ink">
                {completed} / {questions.length}
              </p>
            </div>
            <div className="flex justify-end">
              <Button
                onClick={handleSubmit}
                disabled={submitting || completed !== questions.length}
              >
                {submitting ? "送出中..." : "前往 Zodiac"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
