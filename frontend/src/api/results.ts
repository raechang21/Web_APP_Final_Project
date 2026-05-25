import type {
  DeepAnalysisResponse,
  DiagnosticResponse,
  PlotlyFigure,
  ResultsResponse,
} from "@/types";

import { apiRequest, streamSse } from "./client";

export function fetchResults() {
  return apiRequest<ResultsResponse>("/api/results");
}

export function fetchBigFiveChart() {
  return apiRequest<PlotlyFigure>("/api/big-five-chart");
}

export function fetchDeepAnalysis() {
  return apiRequest<DeepAnalysisResponse>("/api/deep-analysis");
}

export function streamDeepAnalysis(
  onEvent: (event: { chunk?: string; done?: boolean; error?: string }) => void,
) {
  return streamSse("/api/deep-analysis/stream", { method: "GET" }, onEvent);
}

export function fetchDiagnostic() {
  return apiRequest<DiagnosticResponse>("/api/diagnostic");
}

