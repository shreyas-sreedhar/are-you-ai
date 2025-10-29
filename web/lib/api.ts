export type FrameInconsistency = {
  type: string;
  severity: string;
  description: string;
  location?: string;
};

export type FrameAnalysis = {
  confidence_score: number;
  is_likely_fake: boolean;
  inconsistencies: FrameInconsistency[];
  reasoning: string;
};

export type SequenceAnalysis = {
  confidence_score: number;
  is_likely_fake: boolean;
  temporal_inconsistencies: Array<{
    frame_range: string;
    type: string;
    severity: string;
    description: string;
    affected_frames?: number[];
    location?: string;
  }>;
  frame_by_frame_notes?: string[];
  summary?: string;
  reasoning?: string;
};

export type TextAnalysis = {
  overall_verdict: string;
  confidence: number;
  key_findings: string[];
  reasoning: string;
  executive_summary?: string;
};

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function analyzeFrame(frameBase64: string, timestamp = 0): Promise<FrameAnalysis> {
  const res = await fetch(`${BACKEND}/api/v1/analyze-frame`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frame: frameBase64, timestamp })
  });
  if (!res.ok) throw new Error(`analyze-frame failed: ${res.status}`);
  return res.json();
}

export async function analyzeSequence(
  frames: { frame: string; timestamp: number }[],
  video_id?: string,
  video_title?: string
): Promise<SequenceAnalysis> {
  const res = await fetch(`${BACKEND}/api/v1/analyze-sequence`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ frames, video_id, video_title })
  });
  if (!res.ok) throw new Error(`analyze-sequence failed: ${res.status}`);
  return res.json();
}

export async function analyzeText(content: string, title?: string): Promise<TextAnalysis> {
  const res = await fetch(`${BACKEND}/api/v1/analyze-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, title })
  });
  if (!res.ok) throw new Error(`analyze-text failed: ${res.status}`);
  return res.json();
}

export type AvatarResponse = {
  avatar_url: string;
  avatar_type: "image" | "video" | "glb";
  reasoning?: string;
};

export async function generateAvatar(context: string, persona: string = "nvidia_omniverse"): Promise<AvatarResponse | null> {
  try {
    const res = await fetch(`${BACKEND}/api/v1/avatar/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ persona, context })
    });
    if (!res.ok) return null; // optional endpoint; fail soft
    return await res.json();
  } catch {
    return null;
  }
}


