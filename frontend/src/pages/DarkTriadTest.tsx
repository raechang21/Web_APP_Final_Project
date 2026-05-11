import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { fetchDarkTriadQuestions, submitDarkTriad } from "@/api/tests";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FlowSteps } from "@/components/layout/FlowSteps";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { BIG_FIVE_OPTIONS } from "@/lib/personality";
import { cn } from "@/lib/utils";
import { useSessionStore } from "@/store/session";
import type { DarkTriadQuestion } from "@/types";

export default function DarkTriadTest() {
  const navigate = useNavigate();
  const zodiac = useSessionStore((state) => state.zodiac);
  const patchSession = useSessionStore((state) => state.patchSession);
  const [questions, setQuestions] = useState<DarkTriadQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    fetchDarkTriadQuestions()
      .then((response) => {
        if (active) {
          setQuestions(response.questions);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "載入 Dark Triad 題目失敗");
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

  if (!zodiac) {
    return <Navigate to="/zodiac" replace />;
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    try {
      const response = await submitDarkTriad(answers);
      patchSession({ dark_triad_scores: response.dark_triad_scores, has_results: true });
      navigate("/results");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Dark Triad 提交失敗");
    } finally {
      setSubmitting(false);
    }
  }

  const completed = Object.keys(answers).length;

  return (
    <PageShell>
      <FlowSteps />
      <SectionHero
        eyebrow="Optional Step"
        title="這裡不把特質妖魔化，只把它放回行為策略的語境。"
        description="每題都請以你真實的反應作答。這個區塊的分析價值，在於看你如何應對競爭、權威與自我展示。"
      />

      <Card className="sticky top-4 z-10">
        <CardContent className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-stone-500">作答進度</p>
            <h2 className="font-display text-3xl text-ink">
              {completed} / {questions.length}
            </h2>
          </div>
          <Button
            disabled={submitting || completed !== questions.length}
            onClick={handleSubmit}
          >
            {submitting ? "送出中..." : "前往 Results"}
          </Button>
        </CardContent>
      </Card>

      {loading ? <p className="text-stone-500">題目載入中...</p> : null}
      {error ? <p className="text-sm text-red-500">{error}</p> : null}

      <div className="space-y-4">
        {questions.map((question, index) => (
          <Card key={question.id}>
            <CardContent className="space-y-5">
              <div className="flex gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-lavender text-white">
                  {index + 1}
                </div>
                <div>
                  <p className="text-lg font-medium text-ink">{question.text}</p>
                  <p className="mt-1 text-sm text-stone-500">{question.dimension}</p>
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
                          ? "border-lavender bg-lavender text-white"
                          : "border-stone-200 bg-white text-stone-600 hover:border-stone-300",
                      )}
                      onClick={() =>
                        setAnswers((current) => ({
                          ...current,
                          [question.id]: option.value,
                        }))
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
    </PageShell>
  );
}
