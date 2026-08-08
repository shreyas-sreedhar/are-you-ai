/**
 * Shared constants, settings access and icons.
 *
 * Content scripts listed together in the manifest share one global scope, so
 * everything hangs off a single `RUAI` namespace rather than using modules.
 */

(function () {
  "use strict";

  const RUAI = (window.RUAI = window.RUAI || {});

  RUAI.DEFAULTS = Object.freeze({
    backendUrl: "http://localhost:8000",
    videoChecksEnabled: true,
    messageChecksEnabled: true,
  });

  /** How many frames a video check sends. Two or more enables the sequence
   *  check, which is where generated video actually gives itself away. */
  RUAI.FRAME_BURST = 4;
  RUAI.FRAME_GAP_MS = 250;

  /** Short labels for the launcher pill. The sheet carries the full wording. */
  RUAI.RISK_LABEL = Object.freeze({
    safe: "Looks fine",
    caution: "Be careful",
    danger: "Do not trust",
  });

  RUAI.RISK_WORD = Object.freeze({
    safe: "Safe",
    caution: "Caution",
    danger: "Warning",
  });

  // --- Settings ---------------------------------------------------------

  RUAI.settings = {
    async get() {
      const stored = await chrome.storage.local.get(Object.keys(RUAI.DEFAULTS));
      return { ...RUAI.DEFAULTS, ...stored };
    },
    async set(values) {
      await chrome.storage.local.set(values);
    },
  };

  // --- Icons ------------------------------------------------------------
  // Static, first-party markup. Everything derived from a page or a model
  // response is set with textContent instead.

  const svg = (body, extra = "") =>
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
      stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${body}</svg>`;

  RUAI.ICONS = Object.freeze({
    safe: svg('<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/>'),
    caution: svg(
      '<path d="M12 3.6L21 19.2H3L12 3.6z"/><path d="M12 10v4"/><path d="M12 17.2v.01"/>'
    ),
    danger: svg(
      '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.2"/><path d="M12 16.4v.01"/>'
    ),
    check: svg('<path d="M4 12.5l5 5L20 6.5"/>'),
    close: svg('<path d="M6 6l12 12M18 6L6 18"/>'),
    mark: `<svg viewBox="0 0 128 128" aria-hidden="true">
      <path d="M44.3 42.8 A21 21 0 1 1 82.2 60.5 L64 80" fill="none" stroke="#fff"
        stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
      <rect x="57.5" y="91.5" width="13" height="13" rx="3.25" fill="#fff"/>
    </svg>`,
  });

  /**
   * Build an element without ever handing page or model text to innerHTML.
   * The previous build interpolated model output straight into markup.
   */
  RUAI.el = function el(tag, props = {}, children = []) {
    const node = document.createElement(tag);

    for (const [key, value] of Object.entries(props)) {
      if (value === null || value === undefined) continue;
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key === "html") node.innerHTML = value; // first-party icons only
      else if (key === "on") {
        for (const [event, handler] of Object.entries(value)) {
          node.addEventListener(event, handler);
        }
      } else if (key === "style") Object.assign(node.style, value);
      else node.setAttribute(key, value);
    }

    for (const child of [].concat(children)) {
      if (child) node.append(child);
    }
    return node;
  };
})();
