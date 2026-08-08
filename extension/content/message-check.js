/**
 * "Is this message a scam?" on Facebook and Instagram.
 *
 * Chat DOM is hostile: nodes are recycled, classes are generated, and the
 * same message can appear several times as a thread re-renders. So this errs
 * heavily toward doing nothing — a pre-filter runs locally and only messages
 * that already look like fraud are ever sent to the backend.
 */

(function () {
  "use strict";

  const RUAI = window.RUAI;
  const el = RUAI.el;

  const MIN_LENGTH = 25;
  const MAX_CHECKS_PER_MINUTE = 12;
  const RESCAN_INTERVAL_MS = 6000;

  const MESSAGE_SELECTORS = ['[role="row"]', '[data-scope="messages_table"]'];

  const seen = new Set();
  let recentChecks = [];

  const platform = location.hostname.includes("instagram.com") ? "instagram" : "facebook";

  // --- Local pre-filter --------------------------------------------------
  // A deliberately small mirror of the backend's scan. Its only job is to
  // decide whether a message is worth a network round trip.

  const PRE_FILTER = [
    /\bgift cards?\b/i,
    /\bwire transfer\b/i,
    /\b(bitcoin|crypto|usdt)\b/i,
    /\b(western union|moneygram|zelle|cash app)\b/i,
    /\b(one[- ]time code|verification code|security code|otp)\b/i,
    /\b(social security number|ssn|routing number|account number)\b/i,
    /\bpassword\b/i,
    /\b(irs|medicare|social security administration)\b/i,
    /\b(you won|lottery|sweepstakes|claim your prize|inheritance)\b/i,
    /\b(bail money|in jail|arrested|don'?t tell (mom|anyone))\b/i,
    /\b(suspended|frozen|unauthorized access|unusual activity)\b/i,
    /\b(act now|final notice|last chance|expires today|within 24 hours)\b/i,
    /\b(guaranteed (return|profit)|risk[- ]free|double your money)\b/i,
    /\b(bit\.ly|tinyurl|cutt\.ly|rebrand\.ly)\b/i,
  ];

  function looksWorthChecking(text) {
    if (text.length < MIN_LENGTH) return false;
    let hits = 0;
    for (const pattern of PRE_FILTER) {
      if (pattern.test(text)) hits += 1;
      if (hits >= 1) return true;
    }
    return false;
  }

  function withinRateLimit() {
    const cutoff = Date.now() - 60000;
    recentChecks = recentChecks.filter((time) => time > cutoff);
    if (recentChecks.length >= MAX_CHECKS_PER_MINUTE) return false;
    recentChecks.push(Date.now());
    return true;
  }

  // --- Reading the DOM ---------------------------------------------------

  function messageText(node) {
    const clone = node.cloneNode(true);
    clone.querySelectorAll(".ruai-inline").forEach((warning) => warning.remove());
    return clone.textContent.replace(/\s+/g, " ").trim();
  }

  function senderName(node) {
    const link = node.querySelector('[role="link"], a[href*="/messages/"], h4, h5');
    const name = link?.textContent.trim();
    return name && name.length < 80 ? name : "Unknown sender";
  }

  function fingerprint(text) {
    return text.slice(0, 120);
  }

  // --- Warning UI --------------------------------------------------------

  function attachWarning(node, verdict, text) {
    if (node.querySelector(".ruai-inline")) return;

    const isDanger = verdict.risk === "danger";
    const container = el("div", { class: "ruai-root", style: { position: "static" } });

    const actions = el("div", { class: "ruai-inline-actions" }, [
      el("button", {
        type: "button",
        class: "ruai-btn ruai-btn-primary",
        text: "Why is this a warning?",
        on: {
          click: (event) => {
            event.stopPropagation();
            RUAI.view.showSheet(RUAI.view.verdictCard(verdict), {
              label: "Message check result",
            });
          },
        },
      }),
    ]);

    if (isDanger) {
      actions.append(
        el("button", {
          type: "button",
          class: "ruai-btn ruai-btn-quiet",
          text: "Show the message",
          on: {
            click: (event) => {
              event.stopPropagation();
              node.classList.add("ruai-revealed");
              event.currentTarget.remove();
            },
          },
        })
      );
    }

    const warning = el("div", { class: "ruai-inline", "data-risk": verdict.risk, role: "status" }, [
      el("span", {
        html: RUAI.ICONS[verdict.risk] || RUAI.ICONS.caution,
        style: { width: "26px", height: "26px", flex: "0 0 auto", marginTop: "2px" },
      }),
      el("div", { class: "ruai-inline-body" }, [
        el("div", { class: "ruai-inline-title", text: verdict.headline }),
        el("div", { class: "ruai-inline-text", text: verdict.summary }),
        actions,
      ]),
    ]);

    container.append(warning);
    node.prepend(container);

    // The message itself is hidden behind a blur only when RUAI is confident.
    // Hiding on a maybe would train the reader to dismiss the blur.
    if (isDanger) {
      node.querySelectorAll('[dir="auto"]').forEach((part) => {
        if (!part.closest(".ruai-inline")) part.classList.add("ruai-hidden-content");
      });
    }

    recordAlert(verdict, text);
  }

  function recordAlert(verdict, text) {
    chrome.storage.local.get(["alertCount"], (stored) => {
      const alertCount = (stored.alertCount || 0) + 1;
      chrome.storage.local.set({ alertCount });
      chrome.runtime.sendMessage({
        type: "ruai:alert",
        count: alertCount,
        risk: verdict.risk,
      });
    });
  }

  // --- Scanning ----------------------------------------------------------

  async function inspect(node) {
    if (node.dataset.ruaiChecked === "true") return;

    const text = messageText(node);
    if (!text) return;

    const key = fingerprint(text);
    if (seen.has(key)) return;

    if (!looksWorthChecking(text)) {
      node.dataset.ruaiChecked = "true";
      return;
    }

    seen.add(key);
    node.dataset.ruaiChecked = "true";

    if (!withinRateLimit()) return;

    try {
      const verdict = await RUAI.api.checkMessage({
        text: text.slice(0, 4000),
        sender: senderName(node),
        platform,
      });

      // The backend applies the thresholds; the extension only decides
      // whether the answer is worth interrupting someone for.
      if (verdict.risk === "caution" || verdict.risk === "danger") {
        attachWarning(node, verdict, text);
      }
    } catch (error) {
      console.warn("[RUAI] message check failed:", error?.userMessage || error);
    }
  }

  function scan(root = document) {
    for (const selector of MESSAGE_SELECTORS) {
      let nodes;
      try {
        nodes = root.querySelectorAll?.(selector) ?? [];
      } catch {
        continue;
      }
      nodes.forEach(inspect);
    }
  }

  async function init() {
    const settings = await RUAI.settings.get();
    if (!settings.messageChecksEnabled) return;

    new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const added of mutation.addedNodes) {
          if (added.nodeType === Node.ELEMENT_NODE) scan(added);
        }
      }
    }).observe(document.body, { childList: true, subtree: true });

    // Threads render after the observer is attached, and again on navigation.
    setTimeout(() => scan(), 1500);
    setInterval(() => scan(), RESCAN_INTERVAL_MS);
  }

  init();
})();
