/**
 * Popup script for settings and configuration
 */

const DEFAULT_BACKEND_URL = "http://localhost:8000";

// Initialize popup
document.addEventListener("DOMContentLoaded", async () => {
  await loadSettings();
  await checkConnection();

  // Attach event listeners
  document.getElementById("save-btn").addEventListener("click", saveSettings);
  document.getElementById("backend-url").addEventListener("input", debounce(checkConnection, 500));
});

/**
 * Load settings from storage
 */
async function loadSettings() {
  return new Promise((resolve) => {
    chrome.storage.local.get(["backendUrl"], (result) => {
      const url = result.backendUrl || DEFAULT_BACKEND_URL;
      document.getElementById("backend-url").value = url;
      resolve(url);
    });
  });
}

/**
 * Save settings to storage
 */
async function saveSettings() {
  const url = document.getElementById("backend-url").value.trim();

  if (!url) {
    showStatus("error", "URL cannot be empty");
    return;
  }

  try {
    // Validate URL format
    new URL(url);

    await new Promise((resolve) => {
      chrome.runtime.sendMessage(
        { action: "saveBackendUrl", url },
        (response) => {
          if (response?.success) {
            showStatus("success", "Settings saved!");
            setTimeout(() => checkConnection(), 1000);
            resolve();
          } else {
            showStatus("error", "Failed to save settings");
            resolve();
          }
        }
      );
    });
  } catch (error) {
    showStatus("error", "Invalid URL format");
  }
}
// Open dashboard button
document.getElementById("open-dashboard-btn").addEventListener("click", () => {
  chrome.tabs.create({
    url: chrome.runtime.getURL("dashboard/dashboard.html")
  });
});
/**
 * Check backend connection health
 */
async function checkConnection() {
  const url = document.getElementById("backend-url").value.trim() || DEFAULT_BACKEND_URL;

  if (!url) {
    showStatus("unknown", "Enter a backend URL");
    return;
  }

  try {
    // Validate URL format
    new URL(url);

    showStatus("checking", "Checking connection...");

    const response = await fetch(`${url}/api/v1/health`);

    if (response.ok) {
      const data = await response.json();
      if (data.status === "healthy") {
        const nimStatus = data.nim_api_configured ? " (NIM API configured)" : " (NIM API not configured)";
        showStatus("connected", `Connected${nimStatus}`);
      } else {
        showStatus("error", "Backend returned unhealthy status");
      }
    } else {
      showStatus("error", `Connection failed: ${response.status}`);
    }
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("Invalid URL")) {
      showStatus("error", "Invalid URL format");
    } else {
      showStatus("error", "Cannot connect to backend");
    }
  }
}

/**
 * Update status indicator
 */
function showStatus(type, message) {
  const indicator = document.getElementById("status-indicator");
  const dot = indicator.querySelector(".status-dot");
  const text = indicator.querySelector(".status-text");

  // Remove all status classes
  indicator.className = "status-indicator";

  // Add current status class
  indicator.classList.add(`status-${type}`);

  // Update text
  text.textContent = message;

  // Update dot appearance
  dot.className = "status-dot";
  dot.classList.add(`status-dot-${type}`);
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

