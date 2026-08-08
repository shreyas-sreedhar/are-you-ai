"use client";

import { useEffect, useState } from "react";

import type { Verdict } from "../lib/types";
import { CautionIcon, CheckIcon, riskIcon } from "./Brand";

const RISK_WORD: Record<string, string> = {
  safe: "Safe",
  caution: "Caution",
  danger: "Warning",
};

/**
 * The one component that renders an answer.
 *
 * Video, message and article checks all arrive as the same Verdict, so this
 * is the whole presentation layer for results — on this site and, in its
 * vanilla-JS twin, inside the extension.
 */
export function VerdictCard({ verdict }: { verdict: Verdict }) {
  // Grow the bar from zero on mount so the result lands rather than appears.
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const frame = requestAnimationFrame(() =>
      setWidth(Math.max(6, Math.round(verdict.score * 100)))
    );
    return () => cancelAnimationFrame(frame);
  }, [verdict]);

  return (
    <article className="verdict">
      <header className="verdict-head" data-risk={verdict.risk}>
        <div className="verdict-top">
          <div>
            <h3 className="verdict-headline">{verdict.headline}</h3>
            <p className="verdict-summary">{verdict.summary}</p>
          </div>
          <div className="verdict-icon">{riskIcon(verdict.risk)}</div>
        </div>

        {verdict.source && (
          <span className="verdict-source">{verdict.source}</span>
        )}

        {/* A percentage would imply a precision this does not have, so the
            bar is labelled with a word. The number stays in the details. */}
        <div className="meter">
          <div className="meter-label">
            <span>Concern level</span>
            <span>{RISK_WORD[verdict.risk]}</span>
          </div>
          <div
            className="meter-track"
            role="img"
            aria-label={`Concern level: ${RISK_WORD[verdict.risk]}`}
          >
            <div className="meter-fill" style={{ width: `${width}%` }} />
          </div>
        </div>
      </header>

      {verdict.degraded && (
        <div className="verdict-degraded">
          <span style={{ width: 20, flex: "0 0 auto" }}>
            <CautionIcon />
          </span>
          <span>
            This is a quick local check. RUAI&apos;s AI service was not
            reachable.
          </span>
        </div>
      )}

      {verdict.signals.length > 0 && (
        <section className="verdict-section">
          <h4>{verdict.kind === "message" ? "What we noticed" : "What we found"}</h4>
          {verdict.signals.map((signal, index) => (
            <div
              className="signal"
              data-severity={signal.severity}
              key={`${signal.label}-${index}`}
              style={{ animationDelay: `${60 + index * 50}ms` }}
            >
              <span className="signal-dot" />
              <div>
                <div className="signal-label">{signal.label}</div>
                <div className="signal-detail">{signal.detail}</div>
              </div>
            </div>
          ))}
        </section>
      )}

      {verdict.advice.length > 0 && (
        <section className="verdict-section">
          <h4>What to do</h4>
          {verdict.advice.map((line, index) => (
            <div
              className="advice-line"
              key={line}
              style={{ animationDelay: `${60 + index * 50}ms` }}
            >
              <span className="advice-check">
                <CheckIcon />
              </span>
              <span>{line}</span>
            </div>
          ))}
        </section>
      )}

      {verdict.analysis_note && (
        <details className="verdict-note">
          <summary>How RUAI worked this out</summary>
          <p>{verdict.analysis_note}</p>
          <p>Score: {Math.round(verdict.score * 100)} out of 100.</p>
        </details>
      )}
    </article>
  );
}
