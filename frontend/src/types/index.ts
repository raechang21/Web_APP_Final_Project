export type MbtiType =
  | "INTJ"
  | "INTP"
  | "ENTJ"
  | "ENTP"
  | "INFJ"
  | "INFP"
  | "ENFJ"
  | "ENFP"
  | "ISTJ"
  | "ISFJ"
  | "ESTJ"
  | "ESFJ"
  | "ISTP"
  | "ISFP"
  | "ESTP"
  | "ESFP";

export interface BigFiveScores {
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
}

export interface DarkTriadScores {
  machiavellianism: number;
  narcissism: number;
  psychopathy: number;
}

export interface SessionData {
  user_name: string | null;
  mbti: MbtiType | null;
  big_five_scores: BigFiveScores | null;
  zodiac: string | null;
  dark_triad_scores: DarkTriadScores | null;
  has_results: boolean;
  has_analysis: boolean;
  is_quick_login: boolean;
  welcome_message: string | null;
}

export interface BigFiveQuestion {
  id: number;
  original_id: number;
  dimension: keyof BigFiveScores;
  text: string;
  reverse: boolean;
}

export interface DarkTriadQuestion {
  id: number;
  dimension: keyof DarkTriadScores;
  text: string;
  reverse: boolean;
}

export interface MbtiAnalysis {
  nickname?: string;
  title?: string;
  description: string;
  strengths?: string[];
  weaknesses?: string[];
  growth_areas?: string[];
  career_suggestions?: string;
  interaction_style?: string;
}

export interface ZodiacAnalysis {
  emoji?: string;
  description: string;
  strengths?: string[];
  growth_areas?: string[];
  compatibility?: string;
  career?: string;
  interaction?: string;
}

export interface ResultsAnalysis {
  mbti?: MbtiAnalysis;
  big_five?: string;
  zodiac?: ZodiacAnalysis;
  dark_triad?: string | null;
  comprehensive?: string;
}

export interface ResultsResponse {
  mbti: MbtiType;
  big_five_scores: BigFiveScores;
  zodiac: string;
  dark_triad_scores: DarkTriadScores | null;
  analysis: ResultsAnalysis;
}

export interface PlotlyFigure {
  data: Array<Record<string, unknown>>;
  layout: Record<string, unknown>;
}

export interface DeepAnalysisResponse extends ResultsResponse {
  has_analysis: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

export interface ConversationSummary {
  id: number;
  timestamp: string | null;
  message_count: number;
  preview: string;
}

export interface DiagnosticResponse {
  user_name: string | null;
  mbti: string | null;
  big_five_scores: BigFiveScores | null;
  zodiac: string | null;
  dark_triad_scores: DarkTriadScores | null;
  chat_messages_count: number;
  has_analysis: boolean;
  has_comprehensive: boolean;
}
