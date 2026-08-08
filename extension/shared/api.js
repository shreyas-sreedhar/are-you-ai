/**
 * Talking to the RUAI backend.
 *
 * Every failure is translated into a sentence the reader can act on. A user
 * who is being scammed does not benefit from "TypeError: Failed to fetch".
 */

(function () {
  "use strict";

  const RUAI = (window.RUAI = window.RUAI || {});

  const OFFLINE_MESSAGE =
    "RUAI cannot reach its checker. Make sure it is running, then try again.";
  const UNAVAILABLE_MESSAGE =
    "RUAI cannot check this right now. Please try again in a moment.";

  class RuaiError extends Error {
    constructor(userMessage, cause) {
      super(userMessage);
      this.name = "RuaiError";
      this.userMessage = userMessage;
      this.cause = cause;
    }
  }

  async function request(path, { method = "GET", body, timeoutMs = 90000 } = {}) {
    const { backendUrl } = await RUAI.settings.get();
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    let response;
    try {
      response = await fetch(`${backendUrl}${path}`, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
    } catch (error) {
      throw new RuaiError(
        error.name === "AbortError"
          ? "That check took too long. Please try again."
          : OFFLINE_MESSAGE,
        error
      );
    } finally {
      clearTimeout(timer);
    }

    if (response.status === 503) {
      const detail = await readDetail(response);
      throw new RuaiError(detail || UNAVAILABLE_MESSAGE);
    }

    if (!response.ok) {
      throw new RuaiError(
        response.status === 422
          ? "RUAI could not read that. Try again once the video is playing."
          : UNAVAILABLE_MESSAGE,
        new Error(`HTTP ${response.status}`)
      );
    }

    return response.status === 204 ? null : response.json();
  }

  async function readDetail(response) {
    try {
      const body = await response.json();
      return typeof body?.detail === "string" ? body.detail : null;
    } catch {
      return null;
    }
  }

  RUAI.RuaiError = RuaiError;

  RUAI.api = {
    health: () => request("/api/v1/health", { timeoutMs: 4000 }),

    checkVideo: (payload) =>
      request("/api/v1/check/video", { method: "POST", body: payload }),

    checkMessage: (payload) =>
      request("/api/v1/check/message", { method: "POST", body: payload, timeoutMs: 30000 }),

    checkArticle: (payload) =>
      request("/api/v1/check/article", { method: "POST", body: payload }),

    activitySummary: () => request("/api/v1/activity/summary", { timeoutMs: 6000 }),

    recentActivity: (limit = 20) =>
      request(`/api/v1/activity/recent?limit=${limit}`, { timeoutMs: 6000 }),

    clearActivity: () => request("/api/v1/activity", { method: "DELETE" }),
  };
})();
