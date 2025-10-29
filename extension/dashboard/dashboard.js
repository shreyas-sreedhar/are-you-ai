/**
 * Senior Protection Dashboard
 * Displays alerts, metrics, and protection status
 */

(function () {
    "use strict";

    let metrics = {
        videos_protected: 0,
        scams_detected: 0,
        messages_analyzed: 0,
        active_alerts: 0,
    };

    /**
     * Initialize dashboard
     */
    function init() {
        loadMetrics();
        loadAlerts();
        setupEventListeners();

        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadMetrics();
            loadAlerts();
        }, 30000);
    }

    /**
     * Load metrics from storage
     */
    function loadMetrics() {
        chrome.storage.local.get(["metrics", "alerts"], (result) => {
            if (result.metrics) {
                metrics = result.metrics;
            }

            // Count active high/critical alerts
            const alerts = result.alerts || [];
            metrics.active_alerts = alerts.filter(
                (a) => a.risk_level === "CRITICAL" || a.risk_level === "HIGH"
            ).length;

            updateMetricsUI();
        });
    }

    /**
     * Update metrics UI
     */
    function updateMetricsUI() {
        document.getElementById("videos-protected").textContent = metrics.videos_protected || 0;
        document.getElementById("scams-detected").textContent = metrics.scams_detected || 0;
        document.getElementById("messages-analyzed").textContent = metrics.messages_analyzed || 0;
        document.getElementById("active-alerts").textContent = metrics.active_alerts || 0;

        // Update last scan time
        const lastScan = new Date().toLocaleTimeString();
        document.getElementById("last-scan").textContent = lastScan;
    }

    /**
     * Load alerts from storage
     */
    function loadAlerts() {
        chrome.storage.local.get(["alerts"], (result) => {
            const alerts = result.alerts || [];
            displayAlerts(alerts);
        });
    }

    /**
     * Display alerts in the UI
     */
    function displayAlerts(alerts) {
        const container = document.getElementById("alerts-container");

        if (alerts.length === 0) {
            container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">✨</div>
          <div class="empty-text">No alerts yet - you're protected!</div>
        </div>
      `;
            return;
        }

        container.innerHTML = alerts
            .map((alert) => createAlertCard(alert))
            .join("");

        // Add event listeners to action buttons
        container.querySelectorAll(".alert-action-btn").forEach((btn) => {
            btn.addEventListener("click", (e) => {
                const action = e.target.dataset.action;
                const alertId = e.target.dataset.alertId;
                handleAlertAction(action, alertId);
            });
        });
    }

    /**
     * Create alert card HTML
     */
    function createAlertCard(alert) {
        const riskClass = alert.risk_level.toLowerCase();
        const riskEmoji =
            alert.risk_level === "CRITICAL"
                ? "🚨"
                : alert.risk_level === "HIGH"
                    ? "⚠️"
                    : alert.risk_level === "MEDIUM"
                        ? "⚡"
                        : "ℹ️";

        const timeAgo = getTimeAgo(alert.timestamp);

        return `
      <div class="alert-item ${riskClass}" data-alert-id="${alert.id}">
        <div class="alert-header">
          <div class="alert-title">
            <span>${riskEmoji}</span>
            <span>${alert.type === "message" ? "Suspicious Message" : "Suspicious Video"}</span>
            <span class="alert-badge">${alert.risk_level}</span>
          </div>
          <div class="alert-time">${timeAgo}</div>
        </div>

        ${alert.sender ? `
          <div class="alert-sender">
            <strong>From:</strong> ${alert.sender}
            <span class="alert-platform">${alert.platform}</span>
          </div>
        ` : ""}

        <div class="alert-content">
          "${alert.message_preview || alert.video_title || "Content blocked for your protection"}"
        </div>

        ${alert.scam_types && alert.scam_types.length > 0 ? `
          <div style="margin-bottom: 12px; font-size: 13px;">
            <strong style="color: #ff5252;">Detected Scam Type:</strong> 
            ${alert.scam_types.join(", ")}
          </div>
        ` : ""}

        <div class="alert-actions">
          <button class="alert-action-btn" data-action="details" data-alert-id="${alert.id}">
            📋 View Details
          </button>
          <button class="alert-action-btn" data-action="dismiss" data-alert-id="${alert.id}">
            ✓ Dismiss
          </button>
          <button class="alert-action-btn" data-action="report" data-alert-id="${alert.id}">
            🚫 Report Scam
          </button>
        </div>
      </div>
    `;
    }

    /**
     * Get time ago string
     */
    function getTimeAgo(timestamp) {
        const now = new Date();
        const alertTime = new Date(timestamp);
        const diffMs = now - alertTime;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return "Just now";
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`;

        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;

        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
    }

    /**
     * Handle alert actions
     */
    function handleAlertAction(action, alertId) {
        switch (action) {
            case "details":
                showAlertDetails(alertId);
                break;
            case "dismiss":
                dismissAlert(alertId);
                break;
            case "report":
                reportScam(alertId);
                break;
        }
    }

    /**
     * Show detailed alert information
     */
    function showAlertDetails(alertId) {
        chrome.storage.local.get(["alerts"], (result) => {
            const alerts = result.alerts || [];
            const alert = alerts.find((a) => a.id == alertId);

            if (!alert) return;

            const modal = document.createElement("div");
            modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        padding: 20px;
      `;

            modal.innerHTML = `
        <div style="
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 600px;
          max-height: 80vh;
          overflow-y: auto;
        ">
          <h2 style="margin-bottom: 16px; color: #ff5252;">
            ${alert.type === "message" ? "🚨 Scam Message Details" : "🚨 Suspicious Video Details"}
          </h2>

          <div style="background: #fff3f3; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <strong>Risk Level:</strong> ${alert.risk_level}<br>
            <strong>Confidence:</strong> ${(alert.scam_risk_score * 100).toFixed(0)}%<br>
            ${alert.sender ? `<strong>Sender:</strong> ${alert.sender}<br>` : ""}
            <strong>Platform:</strong> ${alert.platform}<br>
            <strong>Time:</strong> ${new Date(alert.timestamp).toLocaleString()}
          </div>

          ${alert.scam_types && alert.scam_types.length > 0 ? `
            <div style="margin-bottom: 16px;">
              <strong>Scam Type(s):</strong><br>
              ${alert.scam_types.map(t => `<span style="display: inline-block; background: #ffebee; padding: 6px 12px; border-radius: 6px; margin: 4px;">${t}</span>`).join("")}
            </div>
          ` : ""}

          <div style="margin-bottom: 16px;">
            <strong>Content:</strong>
            <div style="background: #f5f5f5; padding: 12px; border-radius: 8px; margin-top: 8px;">
              ${alert.message_preview || alert.video_title || "Content hidden for protection"}
            </div>
          </div>

          <div style="background: #e8f5e9; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <strong style="color: #2e7d32;">✅ What You Should Do:</strong>
            <ul style="margin-top: 8px; padding-left: 20px;">
              <li>Do NOT respond to this message</li>
              <li>Do NOT send money or personal information</li>
              <li>Verify independently by calling official numbers</li>
              <li>Show this to a family member if unsure</li>
              <li>Report to the platform and authorities</li>
            </ul>
          </div>

          <div style="display: flex; gap: 12px; margin-top: 20px;">
            <button onclick="this.closest('div[style*=fixed]').remove()" style="
              flex: 1;
              background: #4caf50;
              color: white;
              border: none;
              padding: 12px;
              border-radius: 8px;
              font-weight: 600;
              cursor: pointer;
            ">
              Got It
            </button>
            <button onclick="window.open('https://www.consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams', '_blank')" style="
              flex: 1;
              background: #2196f3;
              color: white;
              border: none;
              padding: 12px;
              border-radius: 8px;
              font-weight: 600;
              cursor: pointer;
            ">
              Learn More
            </button>
          </div>
        </div>
      `;

            document.body.appendChild(modal);

            modal.addEventListener("click", (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
        });
    }

    /**
     * Dismiss an alert
     */
    function dismissAlert(alertId) {
        chrome.storage.local.get(["alerts"], (result) => {
            let alerts = result.alerts || [];
            alerts = alerts.filter((a) => a.id != alertId);

            chrome.storage.local.set({ alerts }, () => {
                loadAlerts();
                loadMetrics();
            });
        });
    }

    /**
     * Report scam to authorities
     */
    function reportScam(alertId) {
        if (confirm("This will open the FTC complaint form. Continue?")) {
            window.open("https://www.ftc.gov/complaint", "_blank");
            dismissAlert(alertId);
        }
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Refresh button
        document.getElementById("refresh-btn").addEventListener("click", () => {
            const icon = document.getElementById("refresh-icon");
            icon.style.animation = "none";
            setTimeout(() => {
                icon.style.animation = "spin 0.5s linear";
            }, 10);

            loadMetrics();
            loadAlerts();
        });

        // Settings button
        document.getElementById("settings-btn").addEventListener("click", () => {
            chrome.runtime.openOptionsPage();
        });

        // Clear all alerts
        document.getElementById("clear-alerts-btn").addEventListener("click", () => {
            if (confirm("Are you sure you want to clear all alerts?")) {
                chrome.storage.local.set({ alerts: [] }, () => {
                    loadAlerts();
                    loadMetrics();
                });
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

