"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

/**
 * Fades content in as it scrolls into view.
 *
 * Uses IntersectionObserver rather than an animation library: one small hook
 * against zero dependencies. Content is visible from the start if the browser
 * lacks the API, so nothing can end up permanently invisible.
 */
export function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.05 }
    );

    observer.observe(node);

    // Belt and braces: nothing stays invisible, whatever the observer does.
    const failsafe = setTimeout(() => setVisible(true), 2500);

    return () => {
      clearTimeout(failsafe);
      observer.disconnect();
    };
  }, []);

  return (
    <div
      ref={ref}
      className={`reveal ${visible ? "is-visible" : ""} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}
