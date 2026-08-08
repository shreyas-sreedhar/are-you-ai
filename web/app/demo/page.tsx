import type { Metadata } from "next";
import Link from "next/link";

import { CheckIcon, riskIcon } from "../../components/Brand";
import { Reveal } from "../../components/Reveal";
import {
  DEMO_ALERTS,
  DEMO_INSIGHTS,
  DEMO_SETTINGS,
  DEMO_SOURCES,
  DEMO_STATS,
  PARENT,
} from "../../lib/demo-data";

export const metadata: Metadata = {
  title: "Family view — RUAI",
  description:
    "Parental controls, pointing the other way. What an adult child sees about the scams their parent was protected from this week.",
};

/**
 * The family view, with sample data.
 *
 * Deliberately a separate page from /dashboard: this one needs no backend,
 * no API key and no setup, so the idea can be shown to someone in ten
 * seconds. The live version at /dashboard is the same design over real data.
 */
export default function DemoPage() {
  return (
    <section className="section">
      <div className="shell">
        <Reveal>
          <div className="demo-banner">
            <span style={{ width: 20, flex: "0 0 auto" }}>
              <CheckIcon />
            </span>
            <span>
              <strong>This is a demonstration.</strong> Bri is not a real
              person and none of these messages were really sent — but every
              one is modelled on a scam that runs against older people on
              Facebook and Instagram every day.{" "}
              <Link href="/dashboard" style={{ textDecoration: "underline" }}>
                See the live version
              </Link>
              .
            </span>
          </div>
        </Reveal>

        <Reveal>
          <span className="eyebrow">Family view</span>
          <h1 className="h-section">Parental controls, pointing the other way</h1>
          <p className="lede" style={{ marginBottom: "var(--ruai-8)" }}>
            Parents spent years watching what their children did online. This is
            the same idea, turned around: a quiet way for adult children to know
            their mum or dad is being looked after, without reading their
            messages or taking their independence away.
          </p>
        </Reveal>

        <Reveal>
          <div className="person">
            <div className="person-avatar" aria-hidden="true">
              {PARENT.name[0]}
            </div>
            <div className="person-main">
              <h1>{PARENT.name}&rsquo;s week</h1>
              <p>
                {PARENT.relationship} · {PARENT.age} · protected since{" "}
                {PARENT.protectedSince} · last checked something{" "}
                {PARENT.lastActive}
              </p>
            </div>
            <span className="person-badge">Protection on</span>
          </div>
        </Reveal>

        <Reveal>
          <div className="grid grid-4" style={{ marginBottom: "var(--ruai-8)" }}>
            {DEMO_STATS.map((stat) => (
              <div className="card" key={stat.label}>
                <span
                  className="figure-value"
                  data-tone={stat.tone === "danger" ? "warning" : undefined}
                  style={
                    stat.tone === "safe"
                      ? {
                          background: "none",
                          WebkitBackgroundClip: "initial",
                          color: "var(--ruai-safe)",
                        }
                      : undefined
                  }
                >
                  {stat.value}
                </span>
                <span className="figure-label">{stat.label}</span>
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal>
          <div className="card" style={{ marginBottom: "var(--ruai-6)" }}>
            <h2
              style={{
                fontSize: "var(--ruai-text-xl)",
                marginBottom: "var(--ruai-2)",
              }}
            >
              What happened this week
            </h2>
            <p
              style={{
                color: "var(--ruai-ink-3)",
                fontSize: "var(--ruai-text-sm)",
                marginBottom: "var(--ruai-5)",
              }}
            >
              Six things RUAI checked, what it said, and what Bri did next.
            </p>

            {DEMO_ALERTS.map((alert) => (
              <article
                className="alert-card"
                data-risk={alert.risk}
                key={alert.id}
              >
                <div className="alert-top">
                  <span className="alert-icon">{riskIcon(alert.risk)}</span>
                  <div className="alert-heading">
                    <h3>{alert.headline}</h3>
                    <span className="alert-when">
                      {alert.when} · {alert.where}
                    </span>
                  </div>
                </div>

                {alert.quote && (
                  <blockquote className="alert-quote">
                    &ldquo;{alert.quote}&rdquo;
                  </blockquote>
                )}

                <div className="alert-told">
                  <span className="alert-told-label">RUAI said</span>
                  <span>{alert.told}</span>
                </div>

                <div className="alert-outcome" data-tone={alert.outcomeTone}>
                  <CheckIcon />
                  <span>{alert.outcome}</span>
                </div>
              </article>
            ))}
          </div>
        </Reveal>

        <div className="grid grid-2" style={{ marginBottom: "var(--ruai-6)" }}>
          <Reveal>
            <div className="card" style={{ height: "100%" }}>
              <h2
                style={{
                  fontSize: "var(--ruai-text-xl)",
                  marginBottom: "var(--ruai-4)",
                }}
              >
                Worth knowing
              </h2>
              <div className="grid" style={{ gap: "var(--ruai-3)" }}>
                {DEMO_INSIGHTS.map((insight) => (
                  <div className="insight" key={insight.title}>
                    <h3>{insight.title}</h3>
                    <p>{insight.body}</p>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>

          <Reveal delay={100}>
            <div className="card" style={{ height: "100%" }}>
              <h2
                style={{
                  fontSize: "var(--ruai-text-xl)",
                  marginBottom: "var(--ruai-2)",
                }}
              >
                Where it reaches her
              </h2>
              <p
                style={{
                  color: "var(--ruai-ink-3)",
                  fontSize: "var(--ruai-text-sm)",
                  marginBottom: "var(--ruai-5)",
                }}
              >
                Of everything flagged this month.
              </p>

              <div className="breakdown">
                {DEMO_SOURCES.map((source) => (
                  <div className="breakdown-row" key={source.label}>
                    <span>{source.label}</span>
                    <span className="breakdown-track">
                      <span
                        className="breakdown-fill"
                        data-tone={source.tone}
                        style={{ width: `${source.share}%` }}
                      />
                    </span>
                    <span className="breakdown-value">{source.share}%</span>
                  </div>
                ))}
              </div>

              <p
                style={{
                  marginTop: "var(--ruai-5)",
                  fontSize: "var(--ruai-text-sm)",
                  color: "var(--ruai-ink-2)",
                }}
              >
                Fake and cloned profiles are the way in. Nearly four out of five
                warnings this month started with an account pretending to be
                someone else.
              </p>
            </div>
          </Reveal>
        </div>

        <Reveal>
          <div className="card">
            <h2
              style={{
                fontSize: "var(--ruai-text-xl)",
                marginBottom: "var(--ruai-2)",
              }}
            >
              What you get told
            </h2>
            <p
              style={{
                color: "var(--ruai-ink-3)",
                fontSize: "var(--ruai-text-sm)",
                marginBottom: "var(--ruai-3)",
              }}
            >
              The hardest part of this design was deciding how much a family
              should be able to see. These are the defaults.
            </p>

            {DEMO_SETTINGS.map((setting) => (
              <div className="setting" key={setting.label}>
                <span>
                  <span className="setting-label">{setting.label}</span>
                  <span className="setting-note">{setting.note}</span>
                </span>
                <span
                  className="switch"
                  data-on={String(setting.on)}
                  role="img"
                  aria-label={setting.on ? "On" : "Off"}
                />
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal>
          <div
            className="card"
            style={{
              marginTop: "var(--ruai-6)",
              textAlign: "center",
              padding: "var(--ruai-10)",
            }}
          >
            <h2
              style={{
                fontSize: "var(--ruai-text-2xl)",
                marginBottom: "var(--ruai-3)",
              }}
            >
              This is the part that is hard to build and easy to explain
            </h2>
            <p
              className="lede"
              style={{ margin: "0 auto var(--ruai-6)", textAlign: "center" }}
            >
              Every family with an ageing parent has had the phone call. RUAI
              exists so that the call comes from you, before the money goes.
            </p>
            <Link href="/try" className="btn btn-primary">
              Try a check yourself
            </Link>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
