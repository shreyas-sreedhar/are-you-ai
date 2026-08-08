/**
 * Dashboard: one timeline of everything RUAI has checked.
 *
 * Reads from the backend's activity log rather than extension storage, so a
 * check made in any tab, on any of the three kinds of content, lands in the
 * same list.
 */

(function () {
  "use strict";

  const RUAI = window.RUAI;
  const el = RUAI.el;

  const KIND_NOUN = { video: "Video", message: "Message", article: "Story" };

  const dom = {
    stats: document.getElementById("stats"),
    timeline: document.getElementById("timeline"),
    lastChecked: document.getElementById("last-checked"),
    refresh: document.getElementById("refresh"),
    clear: document.getElementById("clear"),
  };

  let activeKind = "";

  // --- Time ---------------------------------------------------------------

  function timeAgo(isoString) {
    const then = new Date(isoString);
    if (Number.isNaN(then.getTime())) return "";

    const seconds = Math.max(0, (Date.now() - then.getTime()) / 1000);
    if (seconds < 60) return "Just now";

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} min ago`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;

    const days = Math.floor(hours / 24);
    if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;

    return then.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }

  // --- Rendering ----------------------------------------------------------

  function statCard(value, label, tone) {
    return el("div", { class: "dash-stat", "data-tone": tone || "" }, [
      el("span", { class: "dash-stat-value", text: String(value) }),
      el("span", { class: "dash-stat-label", text: label }),
    ]);
  }

  function renderStats(summary) {
    const warnings = (summary.by_risk?.caution ?? 0) + (summary.by_risk?.danger ?? 0);

    dom.stats.replaceChildren(
      statCard(summary.total_checks ?? 0, "Checks made"),
      statCard(summary.by_kind?.video ?? 0, "Videos"),
      statCard(summary.by_kind?.message ?? 0, "Messages"),
      statCard(warnings, "Warnings raised", warnings > 0 ? "warning" : "")
    );

    dom.lastChecked.textContent = summary.last_checked_at
      ? `Last check ${timeAgo(summary.last_checked_at).toLowerCase()}.`
      : "Everything RUAI has looked at on this computer.";
  }

  function entryRow(entry) {
    const meta = [KIND_NOUN[entry.kind] || "Check", entry.source]
      .filter(Boolean)
      .join(" · ");

    return el(
      "button",
      {
        type: "button",
        class: "dash-entry",
        "data-risk": entry.risk,
        on: {
          click: () =>
            RUAI.view.showSheet(RUAI.view.verdictCard(entry), { label: "Check result" }),
        },
      },
      [
        el("span", {
          class: "dash-entry-icon",
          html: RUAI.ICONS[entry.risk] || RUAI.ICONS.caution,
        }),
        el("span", { class: "dash-entry-main" }, [
          el("span", { class: "dash-entry-title", text: entry.headline }),
          el("span", { class: "dash-entry-meta", text: meta }),
        ]),
        el("span", { class: "dash-entry-when", text: timeAgo(entry.checked_at) }),
      ]
    );
  }

  function renderEmpty(message, note) {
    dom.timeline.replaceChildren(
      el("div", { class: "dash-empty" }, [
        el("div", { class: "dash-empty-mark", html: RUAI.ICONS.check }),
        el("div", { class: "dash-empty-title", text: message }),
        el("div", { class: "dash-empty-note", text: note }),
      ])
    );
  }

  function renderLoading() {
    dom.timeline.replaceChildren(
      ...Array.from({ length: 3 }, () => el("div", { class: "dash-skeleton" }))
    );
  }

  function renderTimeline(entries) {
    const filtered = activeKind
      ? entries.filter((entry) => entry.kind === activeKind)
      : entries;

    if (!filtered.length) {
      renderEmpty(
        entries.length ? "Nothing of this kind yet" : "Nothing checked yet",
        entries.length
          ? "Try another filter, or check something new."
          : "Open a video or a message and RUAI will start keeping track here."
      );
      return;
    }

    dom.timeline.replaceChildren(...filtered.map(entryRow));
  }

  // --- Loading ------------------------------------------------------------

  async function load({ showLoading = true } = {}) {
    if (showLoading) renderLoading();

    try {
      const [summary, entries] = await Promise.all([
        RUAI.api.activitySummary(),
        RUAI.api.recentActivity(50),
      ]);
      renderStats(summary);
      renderTimeline(entries);
    } catch (error) {
      dom.stats.replaceChildren();
      renderEmpty(
        "RUAI is not connected",
        error?.userMessage || "The checker could not be reached."
      );
    }
  }

  // --- Wiring -------------------------------------------------------------

  function init() {
    document.getElementById("brand-mark").innerHTML = RUAI.ICONS.mark;

    dom.refresh.addEventListener("click", () => load());

    dom.clear.addEventListener("click", async () => {
      const confirmed = window.confirm(
        "Clear everything RUAI has checked on this computer? This cannot be undone."
      );
      if (!confirmed) return;

      try {
        await RUAI.api.clearActivity();
        await chrome.storage.local.set({ alertCount: 0 });
        chrome.runtime.sendMessage({ type: "ruai:alerts-cleared" });
        load();
      } catch (error) {
        window.alert(error?.userMessage || "The history could not be cleared.");
      }
    });

    document.querySelectorAll(".dash-filter").forEach((button) => {
      button.addEventListener("click", () => {
        document
          .querySelectorAll(".dash-filter")
          .forEach((other) => other.classList.toggle("is-active", other === button));
        activeKind = button.dataset.kind;
        load({ showLoading: false });
      });
    });

    load();
    // Quiet background refresh so an open tab stays current.
    setInterval(() => load({ showLoading: false }), 30000);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
