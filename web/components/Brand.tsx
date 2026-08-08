/**
 * The RUAI mark and the icon set, kept identical to the extension's.
 * Geometry mirrors brand/ruai-mark.svg.
 */

export function Mark({ size = 32 }: { size?: number }) {
  return (
    <span
      className="mark"
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg viewBox="0 0 128 128">
        <path
          d="M44.3 42.8 A21 21 0 1 1 82.2 60.5 L64 80"
          fill="none"
          stroke="#fff"
          strokeWidth="11"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <rect x="57.5" y="91.5" width="13" height="13" rx="3.25" fill="#fff" />
      </svg>
    </span>
  );
}

const strokeProps = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2.2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

export function SafeIcon() {
  return (
    <svg {...strokeProps}>
      <circle cx="12" cy="12" r="9" />
      <path d="M8 12.5l2.5 2.5L16 9.5" />
    </svg>
  );
}

export function CautionIcon() {
  return (
    <svg {...strokeProps}>
      <path d="M12 3.6L21 19.2H3L12 3.6z" />
      <path d="M12 10v4" />
      <path d="M12 17.2v.01" />
    </svg>
  );
}

export function DangerIcon() {
  return (
    <svg {...strokeProps}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7.5v5.2" />
      <path d="M12 16.4v.01" />
    </svg>
  );
}

export function CheckIcon() {
  return (
    <svg {...strokeProps}>
      <path d="M4 12.5l5 5L20 6.5" />
    </svg>
  );
}

export function riskIcon(risk: string) {
  if (risk === "safe") return <SafeIcon />;
  if (risk === "danger") return <DangerIcon />;
  return <CautionIcon />;
}
