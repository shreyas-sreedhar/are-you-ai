"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { Mark, riskIcon } from "../../components/Brand";
import { VerdictCard } from "../../components/VerdictCard";
import { api } from "../../lib/api";
import type { ActivityEntry, ActivitySummary, Verdict } from "../../lib/types";

const KIND_NOUN: Record<string, string> = {
  video: "Video",
  message: "Message",
  article: "Story",
};

const FILTERS = [
  { kind: "", label: "All" },
  { kind: "video", label: "Videos" },
  { kind: "message", label: "Messages" },
  { kind: "article", label: "Stories" },
];

function timeAgo(iso: string): string {
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return "";

  const seconds = Math.max(0, (Date.now() - then.getTime()) / 1000);
  if (seconds < 60) return "Just now";

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;

  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;

  return then.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<ActivitySummary | null>(null);
  const [entries, setEntries] = useState<ActivityEntry[]>([]);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<ActivityEntry | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [nextSummary, nextEntries] = await Promise.all([
        api.activitySummary(),
        api.recentActivity(50),
      ]);
      setSummary(nextSummary);
      setEntries(nextEntries);
      setError(null);
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const timer = setInterval(() => void load(), 30_000);
    return () => clearInterval(timer);
  }, [load]);

  const visible = useMemo(
    () => (filter ? entries.filter((entry) => entry.kind === filter) : entries),
    [entries, filter]
  );

  const warnings =
    (summary?.by_risk?.caution ?? 0) + (summary?.by_risk?.danger ?? 0);

  return (
    <section className="section">
      <div className="shell">
        <span className="eyebrow">History</span>
        <h1 className="h-section">What RUAI has checked</h1>
        <p className="lede" style={{ marginBottom: "var(--ruai-8)" }}>
          Read from the backend&apos;s local activity log. It never leaves the
          machine that produced it, and ordinary messages are never recorded at
          all.
        </p>

        {summary && (
          <div className="grid grid-4" style={{ marginBottom: "var(--ruai-6)" }}>
            <div className="card">
              <span className="figure-value">{summary.total_checks}</span>
              <span className="figure-label">Checks made</span>
            </div>
            <div className="card">
              <span className="figure-value">
                {summary.by_kind?.video ?? 0}
              </span>
              <span className="figure-label">Videos</span>
            </div>
            <div className="card">
              <span className="figure-value">
                {summary.by_kind?.message ?? 0}
              </span>
              <span className="figure-label">Messages</span>
            </div>
            <div className="card">
              <span
                className="figure-value"
                data-tone={warnings > 0 ? "warning" : undefined}
              >
                {warnings}
              </span>
              <span className="figure-label">Warnings raised</span>
            </div>
          </div>
        )}

        <div className="card">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "var(--ruai-4)",
              flexWrap: "wrap",
              marginBottom: "var(--ruai-4)",
            }}
          >
            <h2 style={{ fontSize: "var(--ruai-text-xl)" }}>Recent checks</h2>
            <div className="demo-tabs" style={{ marginBottom: 0 }}>
              {FILTERS.map((option) => (
                <button
                  key={option.label}
                  type="button"
                  className={`demo-tab ${filter === option.kind ? "is-active" : ""}`}
                  onClick={() => setFilter(option.kind)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {loading && (
            <>
              <div className="skeleton" />
              <div className="skeleton" />
              <div className="skeleton" />
            </>
          )}

          {!loading && error && (
            <div className="empty">
              <div className="empty-mark">
                <Mark size={30} />
              </div>
              <strong>RUAI is not connected</strong>
              <span>{error}</span>
            </div>
          )}

          {!loading && !error && visible.length === 0 && (
            <div className="empty">
              <div className="empty-mark">
                <Mark size={30} />
              </div>
              <strong>
                {entries.length ? "Nothing of this kind yet" : "Nothing checked yet"}
              </strong>
              <span>
                {entries.length
                  ? "Try another filter."
                  : "Run a check and it will appear here."}
              </span>
            </div>
          )}

          {!loading &&
            !error &&
            visible.map((entry, index) => (
              <button
                type="button"
                key={`${entry.checked_at}-${index}`}
                className="entry"
                data-risk={entry.risk}
                onClick={() => setSelected(entry)}
              >
                <span className="entry-icon">{riskIcon(entry.risk)}</span>
                <span className="entry-main">
                  <span className="entry-title">{entry.headline}</span>
                  <span className="entry-meta">
                    {[KIND_NOUN[entry.kind] ?? "Check", entry.source]
                      .filter(Boolean)
                      .join(" · ")}
                  </span>
                </span>
                <span className="entry-when">{timeAgo(entry.checked_at)}</span>
              </button>
            ))}
        </div>

        {selected && (
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Check result"
            onClick={(event) => {
              if (event.target === event.currentTarget) setSelected(null);
            }}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 100,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "var(--ruai-6)",
              background: "rgba(11, 16, 32, 0.42)",
              backdropFilter: "blur(3px)",
            }}
          >
            <div style={{ width: "min(560px, 100%)", maxHeight: "86vh", overflowY: "auto" }}>
              <VerdictCard verdict={selected as unknown as Verdict} />
              <button
                type="button"
                className="btn btn-primary"
                style={{ width: "100%", marginTop: "var(--ruai-4)" }}
                onClick={() => setSelected(null)}
                autoFocus
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
