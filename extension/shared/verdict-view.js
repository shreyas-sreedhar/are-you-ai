/**
 * Rendering a Verdict.
 *
 * One renderer for every surface: the overlay on a video page, the warning
 * beside a message, the popup and the dashboard. Because the backend returns
 * the same shape for all three checks, none of those places needs to know
 * what kind of check produced the answer.
 */

(function () {
  "use strict";

  const RUAI = (window.RUAI = window.RUAI || {});
  const el = RUAI.el;

  // --- Pieces -----------------------------------------------------------

  function mark(size = 28) {
    return el("span", {
      class: "ruai-mark",
      html: RUAI.ICONS.mark,
      style: { width: `${size}px`, height: `${size}px` },
    });
  }

  function riskPill(risk) {
    return el("span", {
      class: "ruai-pill",
      "data-risk": risk,
      text: RUAI.RISK_LABEL[risk] || "Checked",
    });
  }

  function meter(verdict) {
    // A percentage would imply a precision this does not have, so the bar is
    // labelled with a word and the number stays in the technical details.
    const fill = el("div", { class: "ruai-meter-fill" });

    // Always leave a sliver visible so an empty track never reads as "broken".
    const width = `${Math.max(6, Math.round(verdict.score * 100))}%`;
    requestAnimationFrame(() => {
      fill.style.width = width;
    });

    return el("div", { class: "ruai-meter" }, [
      el("div", { class: "ruai-meter-label" }, [
        el("span", { text: "Concern level" }),
        el("span", { text: RUAI.RISK_WORD[verdict.risk] || "" }),
      ]),
      el("div", {
        class: "ruai-meter-track",
        role: "img",
        "aria-label": `Concern level: ${RUAI.RISK_WORD[verdict.risk]}`,
      }, [fill]),
    ]);
  }

  function header(verdict) {
    const parts = [
      el("div", { class: "ruai-verdict-top" }, [
        el("div", {}, [
          el("h2", { class: "ruai-headline", text: verdict.headline }),
          el("p", { class: "ruai-summary", text: verdict.summary }),
        ]),
        el("div", {
          class: "ruai-verdict-icon",
          html: RUAI.ICONS[verdict.risk] || RUAI.ICONS.caution,
        }),
      ]),
    ];

    if (verdict.source) {
      parts.push(el("span", { class: "ruai-source", text: verdict.source }));
    }
    parts.push(meter(verdict));

    return el("div", { class: "ruai-verdict-head", "data-risk": verdict.risk }, parts);
  }

  function signals(verdict) {
    if (!verdict.signals?.length) return null;

    return el("div", { class: "ruai-section" }, [
      el("h3", {
        class: "ruai-section-title",
        text: verdict.kind === "message" ? "What we noticed" : "What we found",
      }),
      el(
        "div",
        { class: "ruai-stagger" },
        verdict.signals.map((signal) =>
          el("div", { class: "ruai-signal", "data-severity": signal.severity }, [
            el("span", { class: "ruai-signal-dot" }),
            el("div", {}, [
              el("div", { class: "ruai-signal-label", text: signal.label }),
              el("div", { class: "ruai-signal-detail", text: signal.detail }),
            ]),
          ])
        )
      ),
    ]);
  }

  function advice(verdict) {
    if (!verdict.advice?.length) return null;

    return el("div", { class: "ruai-section" }, [
      el("h3", { class: "ruai-section-title", text: "What to do" }),
      el(
        "div",
        { class: "ruai-stagger" },
        verdict.advice.map((line) =>
          el("div", { class: "ruai-advice" }, [
            el("span", { class: "ruai-advice-check", html: RUAI.ICONS.check }),
            el("span", { text: line }),
          ])
        )
      ),
    ]);
  }

  function reasoning(verdict) {
    if (!verdict.analysis_note) return null;

    const percent = Math.round(verdict.score * 100);
    return el("details", { class: "ruai-details" }, [
      el("summary", { text: "How RUAI worked this out" }),
      el("p", { text: verdict.analysis_note }),
      el("p", { text: `Score: ${percent} out of 100.` }),
    ]);
  }

  function degradedNotice(verdict) {
    if (!verdict.degraded) return null;
    return el("div", { class: "ruai-notice" }, [
      el("span", { html: RUAI.ICONS.caution, style: { width: "20px", flex: "0 0 auto" } }),
      el("span", { text: "This is a quick local check. RUAI's AI service was not reachable." }),
    ]);
  }

  /** The full verdict body, without any surrounding chrome. */
  function verdictCard(verdict) {
    return el("div", { class: "ruai-verdict" }, [
      header(verdict),
      degradedNotice(verdict),
      signals(verdict),
      advice(verdict),
      reasoning(verdict),
    ]);
  }

  // --- The sheet --------------------------------------------------------

  let openSheet = null;

  function closeSheet() {
    if (!openSheet) return;
    const { scrim, previouslyFocused, onKeyDown } = openSheet;
    document.removeEventListener("keydown", onKeyDown, true);
    scrim.remove();
    openSheet = null;
    previouslyFocused?.focus?.();
  }

  /**
   * Show content in a modal sheet.
   * @param {Node} content
   * @param {{actions?: Array<{label: string, primary?: boolean, onClick?: Function}>}} options
   */
  function showSheet(content, options = {}) {
    closeSheet();

    const previouslyFocused = document.activeElement;

    const scroll = el("div", { class: "ruai-sheet-scroll" }, [content]);
    const sheet = el(
      "div",
      {
        class: "ruai-sheet",
        role: "dialog",
        "aria-modal": "true",
        "aria-label": options.label || "RUAI result",
      },
      [scroll]
    );

    const actions = options.actions || [{ label: "Close", primary: true }];
    const buttons = actions.map((action) =>
      el("button", {
        type: "button",
        class: `ruai-btn ${action.primary ? "ruai-btn-primary" : "ruai-btn-quiet"}`,
        text: action.label,
        on: {
          click: () => {
            if (action.onClick) action.onClick();
            if (action.keepOpen !== true) closeSheet();
          },
        },
      })
    );
    sheet.append(el("div", { class: "ruai-sheet-foot" }, buttons));

    const scrim = el(
      "div",
      {
        class: "ruai-root ruai-scrim",
        on: {
          click: (event) => {
            if (event.target === scrim) closeSheet();
          },
        },
      },
      [sheet]
    );

    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        closeSheet();
        return;
      }
      if (event.key !== "Tab") return;

      // Keep focus inside the dialog.
      const focusable = sheet.querySelectorAll("button, [href], summary, [tabindex]");
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown, true);
    document.body.append(scrim);
    openSheet = { scrim, previouslyFocused, onKeyDown };

    buttons[0]?.focus();
    return { close: closeSheet, sheet };
  }

  // --- States -----------------------------------------------------------

  function workingCard(title, note) {
    return el("div", { class: "ruai-working" }, [
      el("div", { class: "ruai-working-mark", html: RUAI.ICONS.mark }),
      el("div", { class: "ruai-working-title", text: title }),
      el("div", { class: "ruai-working-note", text: note }),
      el("div", { class: "ruai-scan" }),
    ]);
  }

  function messageCard(title, body) {
    return el("div", { class: "ruai-working" }, [
      el("div", { class: "ruai-working-mark", html: RUAI.ICONS.mark }),
      el("div", { class: "ruai-working-title", text: title }),
      el("div", { class: "ruai-working-note", text: body }),
    ]);
  }

  RUAI.view = {
    mark,
    riskPill,
    verdictCard,
    workingCard,
    messageCard,
    showSheet,
    closeSheet,
  };
})();
