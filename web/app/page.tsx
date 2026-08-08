import Link from "next/link";

import { BackendStatus } from "../components/Chrome";
import { Mark } from "../components/Brand";
import { Reveal } from "../components/Reveal";
import { VerdictCard } from "../components/VerdictCard";
import type { Verdict } from "../lib/types";

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
    title: "A video",
    where: "YouTube, Facebook",
    body: "Grabs a short burst of frames and looks for things that cannot physically happen — fingers that merge, signage that dissolves, objects that slide without being pushed.",
  },
  {
    title: "A message",
    where: "Messenger, Instagram",
    body: "Reads the message the way a fraud investigator would: not what it is about, but what it is trying to make you do, and how fast.",
  },
  {
    title: "A story",
    where: "Anything you paste in",
    body: "Takes a forwarded article or a claim and says whether it holds up, or whether it simply cannot be confirmed.",
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
              Built for the people fraud targets hardest
            </span>
            <h1 className="h-display">Ask before you believe it.</h1>
            <p className="lede">
              RUAI checks whether a video was made by AI, whether a message is a
              scam, and whether a story holds up. Then it explains the answer in
              words your grandmother would use, and tells her what to do next.
            </p>
            <div className="hero-actions">
              <Link href="/try" className="btn btn-primary">
                Try a check
              </Link>
              <Link href="#architecture" className="btn btn-ghost">
                How it is built
              </Link>
            </div>
            <p className="hero-note">
              Adults over 60 lose more money per fraud report than any other age
              group, and most of it starts with something on a screen that looked
              real.
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
              They look like three products. They are one, because the answer a
              person needs is identical in all three cases.
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

      <section
        className="section"
        id="architecture"
        style={{ background: "var(--ruai-surface)" }}
      >
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
              Paste a message, a story, or a frame from a video. The same three
              routes the extension uses.
            </p>
            <Link href="/try" className="btn btn-primary">
              Try a check
            </Link>
          </Reveal>
        </div>
      </section>
    </>
  );
}
