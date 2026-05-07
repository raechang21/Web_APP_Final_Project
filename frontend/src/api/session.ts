import type { SessionData } from "@/types";

import { apiRequest } from "./client";

export function fetchSession() {
  return apiRequest<SessionData>("/api/session");
}

export function startSession(name: string) {
  return apiRequest<{ success: boolean; user_name: string; redirect: string }>(
    "/api/session/start",
    {
      method: "POST",
      body: { name },
    },
  );
}

export function quickLogin(name: string) {
  return apiRequest<{ success: boolean; message: string; redirect: string }>(
    "/api/quick-login",
    {
      method: "POST",
      body: { name },
    },
  );
}

export function restartSession() {
  return apiRequest<{ success: boolean }>("/api/restart", { method: "POST" });
}
