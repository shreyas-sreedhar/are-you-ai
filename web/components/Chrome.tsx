"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { api } from "../lib/api";
import { Mark } from "./Brand";

const LINKS = [
  { href: "/", label: "Overview" },
  { href: "/try", label: "Try it" },
  { href: "/dashboard", label: "History" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className="nav">
      <div className="shell nav-inner">
        <Link href="/" className="nav-brand">
          <Mark size={32} />
          <span>RUAI</span>
        </Link>
        <div className="nav-links">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`nav-link ${pathname === link.href ? "is-active" : ""}`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

export function Footer() {
  return (
    <footer className="footer">
      <div className="shell footer-inner">
        <div>
          <strong>RUAI — are you AI?</strong>
          <div>
            A second opinion for the people the internet targets hardest.
          </div>
        </div>
        <div>
          Built with NVIDIA NIM · FastAPI · Next.js · Chrome MV3
        </div>
      </div>
    </footer>
  );
}

/** Live backend status. Honest about being a local-first project. */
export function BackendStatus() {
  const [state, setState] = useState<"checking" | "ready" | "warning" | "offline">(
    "checking"
  );
  const [label, setLabel] = useState("Checking the backend…");

  useEffect(() => {
    let cancelled = false;

    api
      .health()
      .then((health) => {
        if (cancelled) return;
        if (health.model_configured) {
          setState("ready");
          setLabel(`Backend ready · v${health.version}`);
        } else {
          setState("warning");
          setLabel("Backend running, no model key");
        }
      })
      .catch(() => {
        if (cancelled) return;
        setState("offline");
        setLabel("Backend not running");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <span className="status" data-state={state} role="status">
      {label}
    </span>
  );
}
