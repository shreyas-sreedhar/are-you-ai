/**
 * Service worker.
 *
 * Deliberately small: it seeds defaults on install and keeps the toolbar
 * badge in step with the number of warnings raised. Everything else happens
 * in the content scripts, which already have the page they need.
 */

const DEFAULTS = {
  backendUrl: "http://localhost:8000",
  videoChecksEnabled: true,
  messageChecksEnabled: true,
};

chrome.runtime.onInstalled.addListener(async () => {
  const stored = await chrome.storage.local.get(Object.keys(DEFAULTS));
  const missing = Object.fromEntries(
    Object.entries(DEFAULTS).filter(([key]) => stored[key] === undefined)
  );
  if (Object.keys(missing).length) await chrome.storage.local.set(missing);
  await refreshBadge();
});

chrome.runtime.onStartup?.addListener(refreshBadge);

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === "ruai:alert") {
    setBadge(message.count);
  } else if (message?.type === "ruai:alerts-cleared") {
    setBadge(0);
  }
});

async function refreshBadge() {
  const { alertCount = 0 } = await chrome.storage.local.get("alertCount");
  setBadge(alertCount);
}

function setBadge(count) {
  const text = count > 0 ? (count > 99 ? "99+" : String(count)) : "";
  chrome.action.setBadgeText({ text });
  chrome.action.setBadgeBackgroundColor({ color: "#C1262D" });
}
