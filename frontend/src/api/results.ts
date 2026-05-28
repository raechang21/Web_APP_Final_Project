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
  return apiRequest<PlotlyFigure>("/api/bigfive-chart");
}

export function fetchDeepAnalysis() {
  return apiRequest<DeepAnalysisResponse>("/api/deep-analysis");
}

export function streamDeepAnalysis(
  onEvent: (event: {
    chunk?: string;
    done?: boolean;
    error?: string;
    cached?: boolean;
    analysis?: string;
  }) => void,
) {
  return streamSse("/api/deep-analysis/stream", { method: "GET" }, onEvent);
}

export function fetchDiagnostic() {
  return apiRequest<DiagnosticResponse>("/api/diagnostic");
}

export function setupTestData() {
  return apiRequest<{ status: string }>("/api/setup-test-data", {
    method: "POST",
  });
}
