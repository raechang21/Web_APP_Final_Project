import { create } from "zustand";

import { fetchSession } from "@/api/session";
import type { SessionData } from "@/types";

type SessionStatus = "idle" | "loading" | "ready" | "error";

const emptySession: SessionData = {
  user_name: null,
  mbti: null,
  big_five_scores: null,
  zodiac: null,
  dark_triad_scores: null,
  has_results: false,
  has_analysis: false,
  is_quick_login: false,
  welcome_message: null,
};

interface SessionStore extends SessionData {
  status: SessionStatus;
  error: string | null;
  hydrated: boolean;
  setSession: (session: SessionData) => void;
  patchSession: (session: Partial<SessionData>) => void;
  hydrate: () => Promise<void>;
  clear: () => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  ...emptySession,
  status: "idle",
  error: null,
  hydrated: false,
  setSession: (session) =>
    set({
      ...session,
      status: "ready",
      error: null,
      hydrated: true,
    }),
  patchSession: (session) => set((state) => ({ ...state, ...session })),
  hydrate: async () => {
    set((state) => ({
      ...state,
      status: state.hydrated ? state.status : "loading",
      error: null,
    }));
    try {
      const session = await fetchSession();
      set({
        ...session,
        status: "ready",
        error: null,
        hydrated: true,
      });
    } catch (error) {
      set({
        ...emptySession,
        status: "error",
        error: error instanceof Error ? error.message : "Session 載入失敗",
        hydrated: true,
      });
    }
  },
  clear: () =>
    set({
      ...emptySession,
      status: "ready",
      error: null,
      hydrated: true,
    }),
}));
