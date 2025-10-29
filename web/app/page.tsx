"use client";
import { useMemo, useState } from "react";
import clsx from "clsx";
import { analyzeFrame as apiAnalyzeFrame, analyzeText as apiAnalyzeText, generateAvatar } from "../lib/api";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

type FrameResult = {
  confidence_score: number;
  is_likely_fake: boolean;
  inconsistencies: { type: string; severity: string; description: string; location?: string }[];
  reasoning: string;
};

export default function Home() {
  const [tab, setTab] = useState<"video" | "news">("video");
  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 12 }}>AI Detector</h1>
      <p style={{ opacity: 0.8, marginBottom: 16 }}>Detect AI-generated fake videos and fake news using NVIDIA NIM models.</p>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button className={pill(tab === "video")} onClick={() => setTab("video")}>Video</button>
        <button className={pill(tab === "news")} onClick={() => setTab("news")}>News</button>
      </div>

      {tab === "video" ? <VideoPanel /> : <NewsPanel />}
    </main>
  );
}

function pill(active: boolean) {
  return clsx("px-3 py-2 rounded-full text-sm font-bold", active ? "bg-white/10" : "bg-white/5 hover:bg-white/10");
}

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ background: "#121826", border: "1px solid #2b3242", borderRadius: 12, padding: 16 }}>{children}</div>
  );
}

function Badge({ fake }: { fake: boolean }) {
  return (
    <span style={{
      padding: "6px 10px",
      borderRadius: 999,
      fontWeight: 800,
      fontSize: 12,
      letterSpacing: 0.3,
      color: fake ? "#ffe8e8" : "#e8ffe8",
      background: fake ? "#2a1212" : "#132a13",
      border: `1px solid ${fake ? "#4b1f1f" : "#1f3d1f"}`
    }}>{fake ? "AI" : "REAL"}</span>
  );
}

function VideoPanel() {
  const [imageB64, setImageB64] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FrameResult | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [avatar, setAvatar] = useState<{ url: string; type: "image" | "video" | "glb" } | null>(null);

  const handleFile = async (file: File) => {
    const base64 = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const result = reader.result as string;
          // reader returns data URL; split off the header
          const b64 = result.includes(",") ? result.split(",")[1] : result;
          resolve(b64);
        } catch (e) {
          reject(e);
        }
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    setImageB64(base64);
  };

  const submit = async () => {
    if (!imageB64) return;
    setLoading(true);
    setResult(null);
    setAvatar(null);
    try {
      const data = (await apiAnalyzeFrame(imageB64, 0)) as FrameResult;
      setResult(data);
      setAvatarLoading(true);
      const av = await generateAvatar(data.reasoning || "");
      if (av && av.avatar_url) setAvatar({ url: av.avatar_url, type: av.avatar_type });
    } finally {
      setLoading(false);
      setAvatarLoading(false);
    }
  };

  return (
    <Card>
      <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Video Frame Check</h2>
      <p style={{ opacity: 0.8, marginBottom: 12 }}>Upload a frame (JPEG/PNG) to quickly check AI signals. The extension handles live frames.</p>
      <input type="file" accept="image/*" onChange={(e) => e.target.files && handleFile(e.target.files[0])} />
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button
          disabled={!imageB64 || loading}
          onClick={submit}
          className={clsx("px-3 py-2 rounded-full font-bold")}
          style={{
            background: "linear-gradient(135deg, #7cfb6b, #76b900)",
            color: "#0b0e13",
            border: "none",
            boxShadow: "0 0 0 1px #355a14 inset, 0 8px 22px rgba(118,185,0,0.35)",
            opacity: (!imageB64 || loading) ? 0.6 : 1
          }}
        >{loading ? "Analyzing…" : "Analyze Frame"}</button>
        {result && <Badge fake={result.is_likely_fake} />}
      </div>
      {result && (
        <div style={{ marginTop: 14, display: "flex", gap: 16, alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ opacity: 0.85, fontWeight: 700 }}>Confidence: {(result.confidence_score * 100).toFixed(1)}%</div>
            <ul style={{ marginTop: 8 }}>
              {result.inconsistencies?.map((i, idx) => (
                <li key={idx} style={{ marginBottom: 6 }}>
                  <strong style={{ textTransform: "uppercase" }}>{i.severity}</strong> – {i.type}: {i.description}
                </li>
              ))}
            </ul>
            <details style={{ marginTop: 8 }}>
              <summary>Reasoning</summary>
              <pre style={{ whiteSpace: "pre-wrap", opacity: 0.85 }}>{result.reasoning}</pre>
            </details>
          </div>
          <div style={{ width: 320, flexShrink: 0 }}>
            <AvatarViewer loading={avatarLoading} url={avatar?.url} type={avatar?.type} speechText={result.reasoning} />
          </div>
        </div>
      )}
    </Card>
  );
}

function NewsPanel() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    overall_verdict: string;
    confidence: number;
    key_findings: string[];
    reasoning: string;
  } | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [avatar, setAvatar] = useState<{ url: string; type: "image" | "video" | "glb" } | null>(null);

  const analyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    setAvatar(null);
    try {
      // Backend endpoint /api/v1/analyze-text
      const data = await apiAnalyzeText(text);
      setResult(data);
      setAvatarLoading(true);
      const av = await generateAvatar(data.reasoning || "");
      if (av && av.avatar_url) setAvatar({ url: av.avatar_url, type: av.avatar_type });
    } catch (e) {
      setResult({ overall_verdict: "INCONCLUSIVE", confidence: 0.0, key_findings: [], reasoning: String(e) });
    } finally {
      setLoading(false);
      setAvatarLoading(false);
    }
  };

  const verdictFake = useMemo(() => {
    if (!result) return false;
    const v = (result.overall_verdict || "").toUpperCase();
    if (v === "LIKELY_FAKE") return true;
    if (v === "LIKELY_REAL") return false;
    return (result.confidence || 0) > 0.7;
  }, [result]);

  return (
    <Card>
      <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Fake News Check</h2>
      <p style={{ opacity: 0.8, marginBottom: 12 }}>Paste an article paragraph or a claim. The backend will score likelihood of misinformation.</p>
      <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste news text…" style={{ width: "100%", minHeight: 140, background: "#0f1420", color: "#eaf1ff", border: "1px solid #2b3242", borderRadius: 8, padding: 10 }} />
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button
          disabled={loading || !text.trim()}
          onClick={analyze}
          className={clsx("px-3 py-2 rounded-full font-bold")}
          style={{
            background: "linear-gradient(135deg, #7cfb6b, #76b900)",
            color: "#0b0e13",
            border: "none",
            boxShadow: "0 0 0 1px #355a14 inset, 0 8px 22px rgba(118,185,0,0.35)",
            opacity: (loading || !text.trim()) ? 0.6 : 1
          }}
        >{loading ? "Analyzing…" : "Analyze Text"}</button>
        {result && <Badge fake={verdictFake} />}
      </div>
      {result && (
        <div style={{ marginTop: 14, display: "flex", gap: 16, alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ opacity: 0.85, fontWeight: 700 }}>Confidence: {((result.confidence || 0) * 100).toFixed(1)}%</div>
            {result.key_findings?.length ? (
              <ul style={{ marginTop: 8 }}>
                {result.key_findings.map((k, i) => (<li key={i} style={{ marginBottom: 6 }}>{k}</li>))}
              </ul>
            ) : null}
            <details style={{ marginTop: 8 }}>
              <summary>Reasoning</summary>
              <pre style={{ whiteSpace: "pre-wrap", opacity: 0.85 }}>{result.reasoning}</pre>
            </details>
          </div>
          <div style={{ width: 320, flexShrink: 0 }}>
            <AvatarViewer loading={avatarLoading} url={avatar?.url} type={avatar?.type} speechText={result.reasoning} />
          </div>
        </div>
      )}
    </Card>
  );
}

function AvatarViewer({ loading, url, type, speechText }: { loading: boolean; url?: string; type?: "image" | "video" | "glb"; speechText?: string }) {
  if (loading) {
    return (
      <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8, opacity: 0.9 }}>
        <span className={clsx("inline-block w-4 h-4 rounded-full", "animate-pulse")} style={{ background: "#76b900" }} />
        <span>Generating Omniverse avatar…</span>
      </div>
    );
  }
  if (!url) return null;
  return (
    <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ fontWeight: 700, opacity: 0.9 }}>Omniverse Avatar</div>
      {type === "video" ? (
        <video src={url} muted loop autoPlay playsInline style={{ maxWidth: 420, width: "100%", borderRadius: 12, border: "none", outline: "none" }} />
      ) : type === "image" ? (
        <img src={url} alt="Avatar" style={{ maxWidth: 420, width: "100%", borderRadius: 12, border: "none", outline: "none" }} />
      ) : (
        // Inline 3D viewer for GLB using model-viewer web component (integrated, no box)
        <model-viewer
          src={url}
          crossorigin="anonymous"
          ar="false"
          camera-controls
          style={{ width: "100%", maxWidth: 480, height: 320, background: "transparent", border: "none", outline: "none" }}
          autoplay
          exposure="1.0"
          shadow-intensity="0.8"
          interaction-prompt="none"
        ></model-viewer>
      )}
      {speechText ? (
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button
            onClick={() => speak(speechText)}
            className={clsx("px-3 py-2 rounded-full font-bold")}
            style={{
              background: "linear-gradient(135deg, #76b900, #9edc3f)",
              color: "#0b0e13",
              border: "none",
              boxShadow: "0 0 0 1px #385a15 inset, 0 6px 18px rgba(118,185,0,0.25)",
            }}
          >
            Play Explanation
          </button>
          <button
            onClick={() => window.speechSynthesis?.cancel()}
            className={clsx("px-3 py-2 rounded-full font-bold")}
            style={{
              background: "transparent",
              color: "#bcd4ff",
              border: "1px solid #2b3242",
            }}
          >
            Stop
          </button>
        </div>
      ) : null}
    </div>
  );
}

function speak(text: string) {
  try {
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.0;
    utter.pitch = 1.0;
    utter.lang = "en-US";
    window.speechSynthesis?.cancel();
    window.speechSynthesis?.speak(utter);
  } catch {}
}


