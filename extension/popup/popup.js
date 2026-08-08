/**
 * Popup: connection state, what RUAI is watching, and a way in to the
 * dashboard. Settings are secondary and stay folded away.
 */

(function () {
  "use strict";

  const RUAI = window.RUAI;

  const dom = {
    status: document.getElementById("status"),
    statusTitle: document.getElementById("status-title"),
    statusNote: document.getElementById("status-note"),
    video: document.getElementById("toggle-video"),
    message: document.getElementById("toggle-message"),
    stats: document.getElementById("stats"),
    checks: document.getElementById("stat-checks"),
    warnings: document.getElementById("stat-warnings"),
    dashboard: document.getElementById("open-dashboard"),
    url: document.getElementById("backend-url"),
    save: document.getElementById("save-url"),
    hint: document.getElementById("save-hint"),
  };

  function setStatus(state, title, note) {
    dom.status.dataset.state = state;
    dom.statusTitle.textContent = title;
    dom.statusNote.textContent = note;
  }

  async function refreshStatus() {
    setStatus("checking", "Checking the connection…", "One moment.");

    try {
      const health = await RUAI.api.health();
      if (health.model_configured) {
        setStatus("ready", "RUAI is ready", "Everything is working.");
      } else {
        setStatus(
          "warning",
          "Partly working",
          "The checker is running but has no AI key, so only quick local checks will run."
        );
      }
      await refreshStats();
    } catch (error) {
      setStatus(
        "offline",
        "RUAI is not connected",
        error?.userMessage || "The checker could not be reached."
      );
      dom.stats.hidden = true;
    }
  }

  async function refreshStats() {
    try {
      const summary = await RUAI.api.activitySummary();
      dom.checks.textContent = summary.total_checks ?? 0;
      dom.warnings.textContent =
        (summary.by_risk?.caution ?? 0) + (summary.by_risk?.danger ?? 0);
      dom.stats.hidden = false;
    } catch {
      dom.stats.hidden = true;
    }
  }

  async function loadSettings() {
    const settings = await RUAI.settings.get();
    dom.video.checked = settings.videoChecksEnabled;
    dom.message.checked = settings.messageChecksEnabled;
    dom.url.value = settings.backendUrl;
  }

  function hint(text, state) {
    dom.hint.textContent = text;
    if (state) dom.hint.dataset.state = state;
    else delete dom.hint.dataset.state;
  }

  async function saveUrl() {
    const value = dom.url.value.trim().replace(/\/+$/, "");

    try {
      new URL(value);
    } catch {
      hint("That does not look like a web address.", "error");
      return;
    }

    await RUAI.settings.set({ backendUrl: value });
    hint("Saved.");
    setTimeout(() => hint(""), 2500);
    refreshStatus();
  }

  function init() {
    document.getElementById("brand-mark").innerHTML = RUAI.ICONS.mark;

    dom.video.addEventListener("change", () =>
      RUAI.settings.set({ videoChecksEnabled: dom.video.checked })
    );
    dom.message.addEventListener("change", () =>
      RUAI.settings.set({ messageChecksEnabled: dom.message.checked })
    );

    dom.dashboard.addEventListener("click", () => {
      chrome.tabs.create({ url: chrome.runtime.getURL("dashboard/dashboard.html") });
    });

    dom.save.addEventListener("click", saveUrl);
    dom.url.addEventListener("keydown", (event) => {
      if (event.key === "Enter") saveUrl();
    });

    // Opening the popup is an acknowledgement, so the badge resets.
    chrome.storage.local.set({ alertCount: 0 });
    chrome.runtime.sendMessage({ type: "ruai:alerts-cleared" });

    loadSettings().then(refreshStatus);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
