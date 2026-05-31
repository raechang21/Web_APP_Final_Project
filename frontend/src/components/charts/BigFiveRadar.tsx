import { Suspense, lazy } from "react";

import type { PlotlyFigure } from "@/types";

const Plot = lazy(() => import("react-plotly.js"));

export function BigFiveRadar({ figure }: { figure: PlotlyFigure }) {
  return (
    <div className="overflow-hidden rounded-[24px] border border-stone-200 bg-white p-3">
      <Suspense fallback={<div className="p-8 text-center text-sm text-stone-500">圖表載入中...</div>}>
        <Plot
          data={figure.data as never}
          layout={{
            autosize: true,
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
            font: { family: "Noto Sans TC, sans-serif", color: "#37352f" },
            margin: { l: 40, r: 40, t: 48, b: 24 },
            dragmode: false,
            ...figure.layout,
          } as never}
          config={{ displayModeBar: false, responsive: true, staticPlot: true }}
          style={{ width: "100%", height: "100%" }}
        />
      </Suspense>
    </div>
  );
}
