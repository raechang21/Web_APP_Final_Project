import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchDiagnostic, setupTestData } from "@/api/results";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PageShell, SectionHero } from "@/components/layout/PageShell";
import { useSessionStore } from "@/store/session";
import type { DiagnosticResponse } from "@/types";

export default function Diagnostic() {
  const navigate = useNavigate();
  const hydrate = useSessionStore((state) => state.hydrate);
  const [data, setData] = useState<DiagnosticResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const response = await fetchDiagnostic();
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Diagnostic 讀取失敗");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSetup() {
    await setupTestData();
    await hydrate();
    await load();
  }

  return (
    <PageShell>
      <SectionHero
        eyebrow="Diagnostic"
        title="這一頁是給 refactor 過程用的，不是正式使用者旅程。"
        description="當你要 smoke test results、deep-analysis 或 chatbot，而不想每次都重新填表單時，這頁可以直接注入測試 session。"
        actions={
          <>
            <Button variant="secondary" onClick={handleSetup}>
              注入測試資料
            </Button>
            <Button onClick={() => navigate("/results")}>前往 Results</Button>
          </>
        }
      />

      <Card>
        <CardContent>
          {error ? <p className="text-sm text-red-500">{error}</p> : null}
          <pre className="overflow-x-auto rounded-3xl bg-stone-950 p-6 text-sm text-stone-100">
            {JSON.stringify(data, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </PageShell>
  );
}
