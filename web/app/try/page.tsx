"use client";

import { useState } from "react";

import { CautionIcon, Mark } from "../../components/Brand";
import { VerdictCard } from "../../components/VerdictCard";
import { api, ApiError } from "../../lib/api";
import type { CheckKind, Verdict } from "../../lib/types";

const TABS: { kind: CheckKind; label: string }[] = [
  { kind: "message", label: "A message" },
  { kind: "article", label: "A story" },
  { kind: "video", label: "A video frame" },
];

const MESSAGE_SAMPLES = [
  {
    label: "Grandparent scam",
    text: "Grandma it's me, I'm in trouble. I was in a car accident and they're keeping me at the station. I need $2,000 for bail today and my lawyer says gift cards are fastest. Please don't tell mom, I'm so embarrassed.",
  },
  {
    label: "Account suspended",
    text: "FINAL NOTICE: unusual activity was detected on your account and it will be suspended within 24 hours. Verify your identity immediately at bit.ly/acct-verify or call our security line to avoid permanent closure.",
  },
  {
    label: "An ordinary message",
    text: "Hi Mum, the kids absolutely loved the photos you sent. We'll call you on Sunday after lunch. Let me know if you want anything from the shops, I'm going Saturday morning anyway.",
  },
];

const ARTICLE_SAMPLES = [
  {
    label: "Health claim",
    text: "Doctors are furious. A retired chemist has discovered that a common kitchen spice reverses type 2 diabetes in eleven days, and pharmaceutical companies are working to keep it off the shelves. Thousands have already thrown away their medication. Share this before it gets taken down.",
  },
  {
    label: "Ordinary reporting",
    text: "The city council voted 7-2 on Tuesday to extend library opening hours at the two branch locations, beginning in March. The change adds four hours on Saturdays and is funded from the existing parks and culture budget, according to the council's published minutes.",
  },
];

export default function TryPage() {
  const [kind, setKind] = useState<CheckKind>("message");
  const [text, setText] = useState("");
  const [sender, setSender] = useState("");
  const [frame, setFrame] = useState<{ base64: string; preview: string } | null>(
    null
  );
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function switchTab(next: CheckKind) {
    setKind(next);
    setVerdict(null);
    setError(null);
  }

  async function readFile(file: File) {
    setError(null);
    const dataUrl = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(file);
    });
    setFrame({ base64: dataUrl.split(",")[1] ?? "", preview: dataUrl });
    setVerdict(null);
  }

  const ready =
    kind === "video" ? Boolean(frame?.base64) : text.trim().length > 10;

  async function run() {
    if (!ready || busy) return;

    setBusy(true);
    setError(null);
    setVerdict(null);

    try {
      if (kind === "message") {
        setVerdict(await api.checkMessage(text, sender || undefined));
      } else if (kind === "article") {
        setVerdict(await api.checkArticle(text));
      } else if (frame) {
        setVerdict(await api.checkVideoFrame(frame.base64));
      }
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Something went wrong running that check."
      );
    } finally {
      setBusy(false);
    }
  }

  const samples = kind === "message" ? MESSAGE_SAMPLES : ARTICLE_SAMPLES;

  return (
    <section className="section">
      <div className="shell">
        <span className="eyebrow">Live</span>
        <h1 className="h-section">Try a check</h1>
        <p className="lede" style={{ marginBottom: "var(--ruai-8)" }}>
          These are the same three routes the extension calls. The backend has
          to be running locally for them to answer.
        </p>

        <div className="grid grid-2" style={{ alignItems: "start", gap: "var(--ruai-8)" }}>
          <div className="card">
            <div className="demo-tabs" role="tablist" aria-label="What to check">
              {TABS.map((tab) => (
                <button
                  key={tab.kind}
                  type="button"
                  role="tab"
                  aria-selected={kind === tab.kind}
                  className={`demo-tab ${kind === tab.kind ? "is-active" : ""}`}
                  onClick={() => switchTab(tab.kind)}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {kind === "video" ? (
              <>
                <label className="field" htmlFor="frame">
                  A still from a video
                </label>
                <label className="dropzone" htmlFor="frame">
                  <strong>Choose an image</strong>
                  <span>
                    A screenshot of a paused video works. JPEG or PNG.
                  </span>
                </label>
                <input
                  id="frame"
                  type="file"
                  accept="image/*"
                  className="visually-hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    if (file) void readFile(file);
                  }}
                />
                {frame && (
                  <div className="preview-frame">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={frame.preview} alt="The frame being checked" />
                  </div>
                )}
                <p
                  style={{
                    marginTop: "var(--ruai-3)",
                    fontSize: "var(--ruai-text-sm)",
                    color: "var(--ruai-ink-3)",
                  }}
                >
                  In the extension this sends a burst of consecutive frames,
                  which is far more accurate — generated video usually gives
                  itself away between frames rather than within one.
                </p>
              </>
            ) : (
              <>
                {kind === "message" && (
                  <>
                    <label className="field" htmlFor="sender">
                      Who it came from (optional)
                    </label>
                    <input
                      id="sender"
                      className="input"
                      placeholder="Unknown number"
                      value={sender}
                      onChange={(event) => setSender(event.target.value)}
                      style={{ marginBottom: "var(--ruai-4)" }}
                    />
                  </>
                )}

                <label className="field" htmlFor="text">
                  {kind === "message" ? "The message" : "The story or claim"}
                </label>
                <textarea
                  id="text"
                  className="textarea"
                  value={text}
                  placeholder={
                    kind === "message"
                      ? "Paste the message here…"
                      : "Paste a paragraph or a claim here…"
                  }
                  onChange={(event) => setText(event.target.value)}
                />

                <div className="samples">
                  {samples.map((sample) => (
                    <button
                      key={sample.label}
                      type="button"
                      className="sample"
                      onClick={() => {
                        setText(sample.text);
                        setVerdict(null);
                      }}
                    >
                      {sample.label}
                    </button>
                  ))}
                </div>
              </>
            )}

            <div className="demo-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={run}
                disabled={!ready || busy}
              >
                {busy ? "Checking…" : "Check it"}
              </button>
              {(text || frame) && (
                <button
                  type="button"
                  className="btn btn-quiet btn-small"
                  onClick={() => {
                    setText("");
                    setFrame(null);
                    setVerdict(null);
                    setError(null);
                  }}
                >
                  Clear
                </button>
              )}
            </div>

            {error && (
              <div className="error-note" style={{ marginTop: "var(--ruai-4)" }}>
                <span style={{ width: 20, flex: "0 0 auto" }}>
                  <CautionIcon />
                </span>
                <span>{error}</span>
              </div>
            )}
          </div>

          <div>
            {busy && (
              <div className="card working">
                <div className="working-mark" />
                <strong>Looking at it now</strong>
                <span>This usually takes a few seconds.</span>
                <div className="scanbar" />
              </div>
            )}

            {!busy && verdict && <VerdictCard verdict={verdict} />}

            {!busy && !verdict && (
              <div className="card empty">
                <div className="empty-mark">
                  <Mark size={30} />
                </div>
                <strong>The answer appears here</strong>
                <span>
                  Pick one of the examples if you would rather not type
                  anything.
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
