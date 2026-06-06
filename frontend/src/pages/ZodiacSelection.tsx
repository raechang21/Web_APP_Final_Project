import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { fetchZodiacs, submitZodiac } from "@/api/tests";
import { Button } from "@/components/ui/button";
import { FlowSteps } from "@/components/layout/FlowSteps";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { ZODIAC_META } from "@/lib/personality";
import { cn } from "@/lib/utils";
import { useSessionStore } from "@/store/session";

export default function ZodiacSelection() {
  const navigate = useNavigate();
  const patchSession = useSessionStore((state) => state.patchSession);
  const bigfive = useSessionStore((state) => state.bigfive_scores);
  const currentZodiac = useSessionStore((state) => state.zodiac);
  const hasResults = useSessionStore((state) => state.has_results);
  const isLocked = Boolean(currentZodiac);
  const [items, setItems] = useState<string[]>([]);
  const [selected, setSelected] = useState<string | null>(() => {
    try {
      return useSessionStore.getState().zodiac ?? sessionStorage.getItem("zodiac_selected");
    } catch {
      return useSessionStore.getState().zodiac;
    }
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    fetchZodiacs()
      .then((response) => {
        if (active) {
          setItems(response.zodiacs);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "載入星座資料失敗");
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

  if (!bigfive) {
    return <Navigate to="/bigfive" replace />;
  }

  async function handleSubmit() {
    if (isLocked) {
      navigate(hasResults ? "/results" : "/dark-triad-intro");
      return;
    }
    if (!selected) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await submitZodiac(selected);
      patchSession({ zodiac: selected });
      navigate("/dark-triad-intro");
    } catch (err) {
      setError(err instanceof Error ? err.message : "星座儲存失敗");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageShell>
      <FlowSteps />
      <SectionHero
        eyebrow="Step 03"
        title="星座"
        description={
          isLocked
            ? "你已經完成星座選擇，這裡只能查看先前選擇，不能再修改。"
            : " "
        }
      />

      {loading ? <p className="text-stone-500">星座資料載入中...</p> : null}
      {error ? <p className="text-sm text-red-500">{error}</p> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {items.map((sign) => {
          const meta = ZODIAC_META[sign];
          const active = selected === sign;
          return (
            <button
              key={sign}
              type="button"
              disabled={isLocked}
              className={cn(
                "rounded-[28px] border p-6 text-left transition hover:-translate-y-1 disabled:cursor-not-allowed disabled:hover:translate-y-0",
                active
                  ? "border-lavender bg-[rgba(157,132,210,0.15)] ring-2 ring-lavender"
                  : "border-stone-200 bg-paper hover:border-stone-300",
              )}
              onClick={() => {
                if (isLocked) {
                  return;
                }
                setSelected(sign);
                sessionStorage.setItem("zodiac_selected", sign);
              }}
            >
              <div className="text-4xl">{meta?.icon ?? "⭐"}</div>
              <h2 className="mt-4 font-display text-3xl text-ink">{sign}</h2>
              <p className="mt-1 text-sm text-stone-500">
                {meta?.dateRange} · {meta?.element}
              </p>
              <p className="mt-4 text-sm leading-7 text-stone-600">{meta?.trait}</p>
            </button>
          );
        })}
      </div>

      <div className="flex justify-end">
        <Button disabled={!selected || submitting} onClick={handleSubmit}>
          {submitting
            ? "儲存中..."
            : isLocked
              ? hasResults
                ? "查看 Results"
                : "查看 Dark Triad"
              : "前往 Dark Triad"}
        </Button>
      </div>
    </PageShell>
  );
}
