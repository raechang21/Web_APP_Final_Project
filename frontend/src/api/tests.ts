import type {
  BigFiveQuestion,
  BigFiveScores,
  DarkTriadQuestion,
  DarkTriadScores,
  MbtiType,
} from "@/types";

import { apiRequest } from "./client";

export function submitMbti(mbti_type: MbtiType) {
  return apiRequest<{ mbti: MbtiType }>("/api/mbti", {
    method: "POST",
    body: { mbti_type },
  });
}

export function fetchBigFiveQuestions() {
  return apiRequest<{ questions: BigFiveQuestion[]; scale_labels: Record<string, string> }>(
    "/api/bigfive/questions",
  );
}

export function submitBigFive(answers: Record<number, number>) {
  return apiRequest<{ bigfive_scores: BigFiveScores }>("/api/bigfive", {
    method: "POST",
    body: { answers },
  });
}

export function fetchZodiacs() {
  return apiRequest<{ zodiacs: string[] }>("/api/zodiacs");
}

export function submitZodiac(zodiac: string) {
  return apiRequest<{ zodiac: string }>("/api/zodiac", {
    method: "POST",
    body: { zodiac },
  });
}

export function fetchDarkTriadQuestions() {
  return apiRequest<{ questions: DarkTriadQuestion[] }>("/api/dark-triad/questions");
}

export function submitDarkTriad(answers: Record<number, number>) {
  return apiRequest<{ dark_triad_scores: DarkTriadScores }>("/api/dark-triad", {
    method: "POST",
    body: { answers },
  });
}

export function skipDarkTriad() {
  return apiRequest<{ skipped: boolean }>("/api/dark-triad/skip", {
    method: "POST",
  });
}
