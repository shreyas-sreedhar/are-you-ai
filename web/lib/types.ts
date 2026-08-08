/**
 * The shapes the backend returns.
 *
 * These mirror `backend/core/verdict.py`. There is one response type for all
 * three checks, which is why there is one card component to render them.
 */

export type CheckKind = "video" | "message" | "article";
export type Risk = "safe" | "caution" | "danger";
export type Severity = "low" | "medium" | "high";

export interface Signal {
  label: string;
  detail: string;
  severity: Severity;
}

export interface Verdict {
  kind: CheckKind;
  risk: Risk;
  score: number;
  headline: string;
  summary: string;
  signals: Signal[];
  advice: string[];
  source: string | null;
  platform: string | null;
  checked_at: string;
  analysis_note: string | null;
  degraded: boolean;
}

export interface ActivitySummary {
  total_checks: number;
  by_kind: Record<string, number>;
  by_risk: Record<string, number>;
  warnings_last_24h: number;
  last_checked_at: string | null;
}

export interface ActivityEntry
  extends Omit<Verdict, "checked_at" | "kind" | "risk"> {
  checked_at: string;
  kind: string;
  risk: Risk;
}

export interface Health {
  status: string;
  version: string;
  model_configured: boolean;
  activity_log_enabled: boolean;
}
