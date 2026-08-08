/**
 * Backend client.
 *
 * Every failure comes back as a sentence worth showing someone, for the same
 * reason the extension does it: "Failed to fetch" helps nobody.
 */

import type {
  ActivityEntry,
  ActivitySummary,
  Health,
  Verdict,
} from "./types";

export const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

const OFFLINE =
  "The RUAI checker is not reachable. Start the backend and try again.";

export class ApiError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  init?: RequestInit & { timeoutMs?: number }
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), init?.timeoutMs ?? 90_000);

  let response: Response;
  try {
    response = await fetch(`${BACKEND}${path}`, {
      ...init,
      headers: init?.body ? { "Content-Type": "application/json" } : undefined,
      signal: controller.signal,
    });
  } catch (error) {
    throw new ApiError(
      (error as Error).name === "AbortError"
        ? "That check took too long. Please try again."
        : OFFLINE
    );
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    let detail: string | null = null;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* response had no JSON body */
    }
    throw new ApiError(
      detail ?? "RUAI could not complete that check.",
      response.status
    );
  }

  return response.status === 204 ? (null as T) : response.json();
}

export const api = {
  health: () => request<Health>("/api/v1/health", { timeoutMs: 5000 }),

  checkMessage: (text: string, sender?: string) =>
    request<Verdict>("/api/v1/check/message", {
      method: "POST",
      body: JSON.stringify({ text, sender: sender || null, platform: "web" }),
      timeoutMs: 40_000,
    }),

  checkArticle: (text: string, title?: string) =>
    request<Verdict>("/api/v1/check/article", {
      method: "POST",
      body: JSON.stringify({ text, title: title || null }),
    }),

  checkVideoFrame: (imageBase64: string, title?: string) =>
    request<Verdict>("/api/v1/check/video", {
      method: "POST",
      body: JSON.stringify({
        frames: [{ image: imageBase64 }],
        title: title || null,
        platform: "web",
      }),
    }),

  activitySummary: () =>
    request<ActivitySummary>("/api/v1/activity/summary", { timeoutMs: 8000 }),

  recentActivity: (limit = 50) =>
    request<ActivityEntry[]>(`/api/v1/activity/recent?limit=${limit}`, {
      timeoutMs: 8000,
    }),
};
