import Link from "next/link";

import { BackendStatus } from "../components/Chrome";
import { Mark } from "../components/Brand";
import { Reveal } from "../components/Reveal";
import { VerdictCard } from "../components/VerdictCard";
import type { Verdict } from "../lib/types";

/**
 * The award line shown in the hero.
 * TODO: replace with the event's actual name before publishing.
 */
const AWARD = "Hackathon winner";

/** A real response shape, filled with a representative result. */
const SAMPLE: Verdict = {
  kind: "message",
  risk: "danger",
  score: 0.91,
  headline: "This looks like a scam",
  summary:
    "This message behaves the way fraud does: it wants money, secrets, or a fast decision. Please do not reply.",
  signals: [
    {
      label: "Claims a family emergency",
      detail:
        "It says a relative is in trouble and needs money now. This is one of the most common scams aimed at grandparents.",
      severity: "high",
    },
    {
      label: "Asks to pay in a way you cannot undo",
      detail:
        "It asks for gift cards, a wire transfer, or cryptocurrency. Money sent this way can almost never be got back.",
      severity: "high",
    },
    {
      label: "Pushes you to act fast",
      detail:
        "It says you must act immediately. Urgency is there to stop you checking, and real matters can wait.",
      severity: "medium",
    },
  ],
  advice: [
    "Do not reply, and do not send money, gift cards, or bank details.",
    "If it claims to be someone you know, phone them on the number you already have for them.",
    "Show this message to a family member or friend before you do anything.",
  ],
  source: "Unknown sender",
  platform: "facebook",
  checked_at: "2026-01-01T00:00:00Z",
  analysis_note:
    "The sender is unknown, claims a grandchild is in custody, requests payment in gift cards, and asks that no one else be told. Secrecy plus an irreversible payment route is the defining shape of the grandparent scam.",
  degraded: false,
};

const CHECKS = [
  {
    title: "The video in her feed",
    where: "YouTube, Facebook",
    body: "The investment tip from a presenter she recognises. RUAI grabs a burst of frames and looks for things that cannot physically happen — a mouth out of step with the words, a logo that redraws itself, fingers that merge.",
  },
  {
    title: "The message from a friend",
    where: "Messenger, Instagram",
    body: "Except the account is three weeks old and the photo is her cousin's. RUAI reads it the way a fraud investigator would: not what it is about, but what it is trying to make her do, and how fast.",
  },
  {
    title: "The story she was forwarded",
    where: "Anything pasted in",
    body: "The one that has been round the family WhatsApp twice. RUAI says whether it holds up, or — just as often, and just as usefully — that it simply cannot be confirmed.",
  },
];

const PRINCIPLES = [
  {
    title: "Three levels, never a percentage",
    body: "“73% likely fake” is a number the reader has to interpret. Safe, Be careful and Do not trust are answers they can act on. The number is still there, folded away, for anyone who wants it.",
  },
  {
    title: "Confidence has to be earned",
    body: "Vision models will happily return 0.8 and then point at nothing. RUAI caps the score at what the model's own evidence supports, which is what stopped ordinary cooking videos coming back flagged.",
  },
  {
    title: "Every answer says what to do next",
    body: "Knowing a message is a scam does not help at nine at night when the caller says your grandson is in jail. Every verdict ends with concrete steps, down to which phone number to use.",
  },
  {
    title: "It answers even when the AI is down",
    body: "A scam warning that arrives after the money is gone is worthless. If the model is unreachable, a local pattern scan answers instead — and the verdict says plainly that it did.",
  },
  {
    title: "Colour is never the only signal",
    body: "Risk is shown as a colour, an icon and a word together, at 17px minimum, with 48px targets. Roughly one in twelve men cannot rely on the red.",
  },
  {
    title: "Nothing leaves the machine",
    body: "The history of what someone watched and who messaged them stays in a local file. Ordinary messages are never logged at all — a record of everything you receive is surveillance, not protection.",
  },
];

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="shell hero-inner">
          <Reveal>
            <span className="eyebrow hero-eyebrow">
              {AWARD} · AI for the people fraud targets hardest
            </span>
            <h1 className="h-display">
              Someone is pretending to be your mother&rsquo;s cousin.
            </h1>
            <p className="lede">
              Our parents only recently discovered social media. The people
              targeting them have been there for twenty years, and have got
              very good at it. A cloned profile. A grandchild in trouble who
              needs gift cards tonight. A news presenter who never said those
              words. RUAI checks whether what they are looking at is real,
              explains it in plain words, and tells them what to do next.
            </p>
            <div className="hero-actions">
              <Link href="/demo" className="btn btn-primary">
                See what a family sees
              </Link>
              <Link href="/try" className="btn btn-ghost">
                Try a check
              </Link>
            </div>
            <p className="hero-note">
              This won its hackathon on the clarity of the problem combined
              with the cleverness of the open-source NVIDIA models underneath
              it. Everyone in the room had the same story about a parent, an
              aunt, a grandfather — and about the phone call that came too late.
            </p>
          </Reveal>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <Reveal>
            <span className="eyebrow">One question</span>
            <h2 className="h-section">
              &ldquo;Is this real?&rdquo; comes up in three places
            </h2>
            <p className="lede">
              They look like three products. They are one, because the answer an
              80-year-old needs is identical in all three cases: is it real,
              how do you know, and what should I do now.
            </p>
          </Reveal>

          <div className="grid grid-3" style={{ marginTop: "var(--ruai-8)" }}>
            {CHECKS.map((check, index) => (
              <Reveal key={check.title} delay={index * 80}>
                <article className="card card-lift" style={{ height: "100%" }}>
                  <h3 style={{ fontSize: "var(--ruai-text-xl)" }}>
                    {check.title}
                  </h3>
                  <p
                    style={{
                      color: "var(--ruai-ink-3)",
                      fontSize: "var(--ruai-text-sm)",
                      marginBottom: "var(--ruai-3)",
                    }}
                  >
                    {check.where}
                  </p>
                  <p style={{ color: "var(--ruai-ink-2)" }}>{check.body}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ background: "var(--ruai-surface)" }}>
        <div className="shell">
          <div className="grid grid-2" style={{ gap: "var(--ruai-12)" }}>
            <Reveal>
              <span className="eyebrow">One answer</span>
              <h2 className="h-section">
                Three analysers. One thing they are allowed to return.
              </h2>
              <p className="lede" style={{ marginBottom: "var(--ruai-6)" }}>
                Every check produces the same <code>Verdict</code>: a risk
                level, a headline, the evidence behind it, and what to do. The
                analysers differ. The answer does not — which is why there is
                one card component in this whole product.
              </p>

              <div className="pipeline">
                <div className="pipeline-column">
                  <div className="pipeline-node">
                    <Mark size={26} />
                    <span>
                      Video frames
                      <small>Vision model, sequence prompt</small>
                    </span>
                  </div>
                  <div className="pipeline-node">
                    <Mark size={26} />
                    <span>
                      Message text
                      <small>Text model + local pattern scan</small>
                    </span>
                  </div>
                  <div className="pipeline-node">
                    <Mark size={26} />
                    <span>
                      Article text
                      <small>Text model, fact-check prompt</small>
                    </span>
                  </div>
                </div>
                <div className="pipeline-arrow" aria-hidden="true">
                  →
                </div>
                <div className="pipeline-target">
                  <strong>Verdict</strong>
                  <span>
                    risk · score · headline · signals · advice
                  </span>
                </div>
              </div>
            </Reveal>

            <Reveal delay={120}>
              <VerdictCard verdict={SAMPLE} />
            </Reveal>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <div className="grid grid-2" style={{ gap: "var(--ruai-12)", alignItems: "center" }}>
            <Reveal>
              <span className="eyebrow">The family view</span>
              <h2 className="h-section">
                Parental controls, for our parents
              </h2>
              <p className="lede" style={{ marginBottom: "var(--ruai-5)" }}>
                Our parents spent years watching what we did online. This turns
                that around. A son or daughter gets a quiet weekly view of what
                their mum was protected from — which scams reached her, what
                RUAI told her, and what she did next.
              </p>
              <p style={{ color: "var(--ruai-ink-2)", marginBottom: "var(--ruai-6)" }}>
                Without reading her messages, and without taking her
                independence away. The defaults were the hardest design problem
                in the project: she is told whenever the family is told, and
                nobody sees the text of a message unless she shares it.
              </p>
              <Link href="/demo" className="btn btn-primary">
                See the family view
              </Link>
              <p
                style={{
                  marginTop: "var(--ruai-3)",
                  fontSize: "var(--ruai-text-sm)",
                  color: "var(--ruai-ink-3)",
                }}
              >
                Sample data. No setup, no backend, no account.
              </p>
            </Reveal>

            <Reveal delay={120}>
              <div className="card" style={{ padding: "var(--ruai-5)" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "var(--ruai-4)",
                    paddingBottom: "var(--ruai-4)",
                    borderBottom: "1px solid var(--ruai-line)",
                    marginBottom: "var(--ruai-4)",
                  }}
                >
                  <span
                    style={{
                      display: "grid",
                      placeItems: "center",
                      width: 48,
                      height: 48,
                      borderRadius: "50%",
                      background: "var(--ruai-gradient)",
                      color: "#fff",
                      fontWeight: 750,
                      fontSize: "var(--ruai-text-xl)",
                    }}
                    aria-hidden="true"
                  >
                    R
                  </span>
                  <div>
                    <strong style={{ fontSize: "var(--ruai-text-lg)" }}>
                      Bri&rsquo;s week
                    </strong>
                    <div
                      style={{
                        fontSize: "var(--ruai-text-sm)",
                        color: "var(--ruai-ink-3)",
                      }}
                    >
                      Your mother · 78 · protection on
                    </div>
                  </div>
                </div>

                {[
                  {
                    risk: "danger",
                    text: "Someone copied her cousin Margaret's profile and asked for $400 in gift cards.",
                    outcome: "She rang the real Margaret. Margaret was at home.",
                  },
                  {
                    risk: "danger",
                    text: "An investment video using a deepfaked news presenter.",
                    outcome: "She read the warning and scrolled past.",
                  },
                  {
                    risk: "caution",
                    text: "A three-week-old account has become very affectionate very quickly.",
                    outcome: "Still talking. Worth a gentle conversation.",
                  },
                ].map((row) => (
                  <div
                    key={row.text}
                    style={{
                      display: "flex",
                      gap: "var(--ruai-3)",
                      padding: "var(--ruai-3) 0",
                    }}
                  >
                    <span
                      style={{
                        flex: "0 0 auto",
                        width: 10,
                        height: 10,
                        marginTop: 8,
                        borderRadius: "50%",
                        background:
                          row.risk === "danger"
                            ? "var(--ruai-danger)"
                            : "var(--ruai-caution)",
                      }}
                    />
                    <div>
                      <div
                        style={{
                          fontSize: "var(--ruai-text-sm)",
                          fontWeight: 600,
                        }}
                      >
                        {row.text}
                      </div>
                      <div
                        style={{
                          fontSize: "var(--ruai-text-sm)",
                          color: "var(--ruai-safe)",
                          marginTop: 2,
                        }}
                      >
                        {row.outcome}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: "var(--ruai-surface)" }}>
        <div className="shell">
          <Reveal>
            <span className="eyebrow">Decisions</span>
            <h2 className="h-section">Six choices that shaped it</h2>
            <p className="lede">
              Most of the work in this project was not the model call. It was
              deciding what a frightened seventy-eight-year-old should see.
            </p>
          </Reveal>

          <div className="grid grid-3" style={{ marginTop: "var(--ruai-8)" }}>
            {PRINCIPLES.map((principle, index) => (
              <Reveal key={principle.title} delay={(index % 3) * 80}>
                <article className="card card-lift" style={{ height: "100%" }}>
                  <h3
                    style={{
                      fontSize: "var(--ruai-text-lg)",
                      marginBottom: "var(--ruai-3)",
                    }}
                  >
                    {principle.title}
                  </h3>
                  <p style={{ color: "var(--ruai-ink-2)" }}>{principle.body}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="section" id="architecture">
        <div className="shell">
          <Reveal>
            <span className="eyebrow">Architecture</span>
            <h2 className="h-section">How it is put together</h2>
          </Reveal>

          <div className="grid grid-2" style={{ marginTop: "var(--ruai-6)" }}>
            <Reveal>
              <article className="card">
                <h3
                  style={{
                    fontSize: "var(--ruai-text-lg)",
                    marginBottom: "var(--ruai-3)",
                  }}
                >
                  Backend — FastAPI
                </h3>
                <ul
                  style={{
                    listStyle: "none",
                    display: "grid",
                    gap: "var(--ruai-2)",
                    color: "var(--ruai-ink-2)",
                    fontSize: "var(--ruai-text-sm)",
                  }}
                >
                  <li>
                    <code>core/</code> — the Verdict, the copy, the prompts, the
                    calibration rule
                  </li>
                  <li>
                    <code>services/</code> — one analyser per check, plus the
                    NIM client
                  </li>
                  <li>
                    <code>storage/</code> — one append-only local activity log
                  </li>
                  <li>
                    <code>api/</code> — three symmetric routes
                  </li>
                  <li>117 tests over parsing, scoring, storage and HTTP</li>
                </ul>
              </article>
            </Reveal>

            <Reveal delay={100}>
              <article className="card">
                <h3
                  style={{
                    fontSize: "var(--ruai-text-lg)",
                    marginBottom: "var(--ruai-3)",
                  }}
                >
                  Extension — Chrome MV3
                </h3>
                <ul
                  style={{
                    listStyle: "none",
                    display: "grid",
                    gap: "var(--ruai-2)",
                    color: "var(--ruai-ink-2)",
                    fontSize: "var(--ruai-text-sm)",
                  }}
                >
                  <li>
                    <code>content/video-check.js</code> — frame burst capture
                  </li>
                  <li>
                    <code>content/message-check.js</code> — local pre-filter,
                    rate limited
                  </li>
                  <li>
                    <code>shared/verdict-view.js</code> — the same card, in
                    vanilla DOM
                  </li>
                  <li>Design tokens generated from the same source as this site</li>
                  <li>No page or model text ever reaches innerHTML</li>
                </ul>
              </article>
            </Reveal>
          </div>

          <Reveal delay={160}>
            <div
              className="card"
              style={{
                marginTop: "var(--ruai-5)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "var(--ruai-4)",
                flexWrap: "wrap",
              }}
            >
              <div>
                <strong>Models: NVIDIA NIM</strong>
                <p
                  style={{
                    color: "var(--ruai-ink-2)",
                    fontSize: "var(--ruai-text-sm)",
                  }}
                >
                  Nemotron Nano 12B VL reads frames. Nemotron Nano 9B reads text
                  — small and fast, because a warning that arrives late is not a
                  warning.
                </p>
              </div>
              <BackendStatus />
            </div>
          </Reveal>
        </div>
      </section>

      <section className="section-tight">
        <div className="shell shell-narrow" style={{ textAlign: "center" }}>
          <Reveal>
            <h2 className="h-section">See it answer something</h2>
            <p className="lede" style={{ margin: "0 auto var(--ruai-6)" }}>
              Paste in the message your mum forwarded you last week. The same
              three routes the extension uses, running live.
            </p>
            <div
              style={{
                display: "flex",
                gap: "var(--ruai-3)",
                justifyContent: "center",
                flexWrap: "wrap",
              }}
            >
              <Link href="/try" className="btn btn-primary">
                Try a check
              </Link>
              <Link href="/demo" className="btn btn-quiet">
                See the family view
              </Link>
            </div>
          </Reveal>
        </div>
      </section>
    </>
  );
}
