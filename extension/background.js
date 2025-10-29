/**
 * Background service worker for AI Video Fakeness Detector
 * Handles extension lifecycle and message passing
 */

// Default backend URL
const DEFAULT_BACKEND_URL = "http://localhost:8000";

// Initialize extension storage with default settings
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["backendUrl"], (result) => {
    if (!result.backendUrl) {
      chrome.storage.local.set({ backendUrl: DEFAULT_BACKEND_URL });
    }
  });
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getBackendUrl") {
    chrome.storage.local.get(["backendUrl"], (result) => {
      sendResponse({ backendUrl: result.backendUrl || DEFAULT_BACKEND_URL });
    });
    return true; // Keep channel open for async response
  }

  if (request.action === "saveBackendUrl") {
    chrome.storage.local.set({ backendUrl: request.url }, () => {
      sendResponse({ success: true });
    });
    return true;
  }

  if (request.action === "healthCheck") {
    checkBackendHealth(request.backendUrl)
      .then((isHealthy) => {
        sendResponse({ isHealthy });
      })
      .catch((error) => {
        sendResponse({ isHealthy: false, error: error.message });
      });
    return true;
  }
});

/**
 * Check if backend API is healthy
 */
async function checkBackendHealth(backendUrl) {
  try {
    const response = await fetch(`${backendUrl}/api/v1/health`);
    if (response.ok) {
      const data = await response.json();
      return data.status === "healthy";
    }
    return false;
  } catch (error) {
    console.error("Backend health check failed:", error);
    return false;
  }
}

