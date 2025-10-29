/**
 * Message Monitor for Senior Protection
 * Monitors Facebook Messenger and other social media messages for scams
 */

(function () {
    "use strict";

    let backendUrl = "http://localhost:8000";
    let messageScans = [];
    let alertCount = 0;

    console.log("[SENIOR PROTECTION] Message monitor initialized");

    // Get backend URL from storage
    chrome.runtime.sendMessage({ action: "getBackendUrl" }, (response) => {
        backendUrl = response?.backendUrl || "http://localhost:8000";
    });

    /**
     * Initialize message monitoring
     */
    function init() {
        // Monitor Facebook Messenger
        if (window.location.hostname.includes("facebook.com")) {
            monitorFacebookMessages();
        }

        // Monitor Instagram DMs
        if (window.location.hostname.includes("instagram.com")) {
            monitorInstagramMessages();
        }
    }

    /**
     * Monitor Facebook Messenger for scam messages
     */
    function monitorFacebookMessages() {
        console.log("[SENIOR PROTECTION] Monitoring Facebook messages...");

        // Multiple detection strategies for different Facebook UIs
        const messageSelectors = [
            '[role="row"]',                                  // Messenger main
            '[data-scope="messages_table"]',                // Old messenger
            '.x1n2onr6',                                     // Message bubbles
            '[aria-label*="Message"]',                       // Aria labeled messages
            'div[dir="auto"][style*="text-align"]',         // Text containers
        ];

        let scannedMessages = new Set();

        // Observe message container for new messages
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) {
                        // Try all selectors
                        messageSelectors.forEach(selector => {
                            try {
                                const messages = node.querySelectorAll ?
                                    node.querySelectorAll(selector) : [];
                                messages.forEach((message) => {
                                    // Avoid duplicate scanning
                                    const msgId = getMessageId(message);
                                    if (!scannedMessages.has(msgId)) {
                                        scannedMessages.add(msgId);
                                        analyzeMessage(message);
                                    }
                                });

                                // Check the node itself
                                if (node.matches && node.matches(selector)) {
                                    const msgId = getMessageId(node);
                                    if (!scannedMessages.has(msgId)) {
                                        scannedMessages.add(msgId);
                                        analyzeMessage(node);
                                    }
                                }
                            } catch (e) {
                                // Selector might not work, continue
                            }
                        });
                    }
                });
            });
        });

        // Start observing the main content area
        const observeTarget = document.querySelector('[role="main"]') ||
            document.querySelector('#mount_0_0') ||
            document.body;

        console.log("[SENIOR PROTECTION] Observing:", observeTarget.tagName);

        observer.observe(observeTarget, {
            childList: true,
            subtree: true,
        });

        // Scan existing messages periodically
        function scanExistingMessages() {
            console.log("[SENIOR PROTECTION] Scanning existing messages...");
            messageSelectors.forEach(selector => {
                try {
                    const messages = document.querySelectorAll(selector);
                    console.log(`[SENIOR PROTECTION] Found ${messages.length} messages with selector: ${selector}`);
                    messages.forEach((message) => {
                        const msgId = getMessageId(message);
                        if (!scannedMessages.has(msgId)) {
                            scannedMessages.add(msgId);
                            analyzeMessage(message);
                        }
                    });
                } catch (e) {
                    // Continue
                }
            });
        }

        // Initial scan after delays (Facebook loads dynamically)
        setTimeout(scanExistingMessages, 2000);
        setTimeout(scanExistingMessages, 5000);
        setInterval(scanExistingMessages, 10000); // Re-scan every 10s
    }

    /**
     * Generate unique ID for a message to avoid duplicates
     */
    function getMessageId(element) {
        const text = extractMessageText(element);
        const timestamp = element.querySelector('time')?.getAttribute('datetime') || Date.now();
        return `${text.substring(0, 50)}-${timestamp}`;
    }

    /**
     * Monitor Instagram DMs
     */
    function monitorInstagramMessages() {
        console.log("[SENIOR PROTECTION] Monitoring Instagram messages...");
        // Similar implementation for Instagram
        // For now, we'll focus on Facebook
    }

    /**
     * Analyze a message element for scam indicators
     */
    async function analyzeMessage(messageElement) {
        try {
            // Extract message text
            const messageText = extractMessageText(messageElement);

            if (!messageText || messageText.length < 10) {
                return; // Skip very short messages
            }

            // Skip if already analyzed
            if (messageElement.dataset.scamAnalyzed === "true") {
                return;
            }
            messageElement.dataset.scamAnalyzed = "true";

            // Extract sender info
            const senderInfo = extractSenderInfo(messageElement);

            // Quick local check for obvious scam keywords
            const quickCheck = performQuickCheck(messageText);

            if (quickCheck.suspicious) {
                // Analyze with backend
                const analysis = await analyzeWithBackend(messageText, senderInfo);

                // Show warning for MEDIUM, HIGH, or CRITICAL risk
                if (analysis.risk_level === "MEDIUM" || analysis.risk_level === "HIGH" ||
                    analysis.risk_level === "CRITICAL" || analysis.scam_risk_score >= 0.4) {
                    // Show warning on the message
                    addWarningToMessage(messageElement, analysis);

                    // Log the alert
                    logAlert(messageText, analysis, senderInfo);

                    // Send alert to dashboard
                    sendAlertToDashboard(messageText, analysis, senderInfo);
                }
            }
        } catch (error) {
            console.error("[SENIOR PROTECTION] Error analyzing message:", error);
        }
    }

    /**
     * Extract text from message element
     */
    function extractMessageText(element) {
        // Try multiple strategies to extract text from Facebook's complex DOM
        let text = "";

        // Strategy 1: Look for specific text containers
        const textSelectors = [
            '[dir="auto"]',
            '[data-lexical-text="true"]',
            '.x1lliihq',
            '.x1a2a7pz',
            'div[style*="text-align"]',
            'span[dir="auto"]',
        ];

        for (const selector of textSelectors) {
            const textElements = element.querySelectorAll(selector);
            if (textElements.length > 0) {
                textElements.forEach((el) => {
                    // Skip if it's a warning we added
                    if (!el.closest('.senior-protection-warning')) {
                        text += el.textContent + " ";
                    }
                });
                if (text.trim()) break;
            }
        }

        // Strategy 2: Fallback to direct text content (excluding our warnings)
        if (!text.trim()) {
            const clone = element.cloneNode(true);
            // Remove our warnings from clone
            clone.querySelectorAll('.senior-protection-warning').forEach(el => el.remove());
            text = clone.textContent;
        }

        // Clean up text
        text = text
            .replace(/\s+/g, ' ')  // Normalize whitespace
            .replace(/[^\x20-\x7E\s]/g, '') // Remove non-printable chars
            .trim();

        return text;
    }

    /**
     * Extract sender information
     */
    function extractSenderInfo(element) {
        // Try to find sender name
        let senderName = "Unknown";
        const nameElement = element.querySelector('[role="link"]') ||
            element.querySelector('a[href*="/messages/"]');

        if (nameElement) {
            senderName = nameElement.textContent.trim();
        }

        return {
            name: senderName,
            verified: false, // Could check for verification badge
            platform: "facebook",
        };
    }

    /**
     * Perform quick local check for scam keywords
     */
    function performQuickCheck(text) {
        const textLower = text.toLowerCase();

        const SCAM_KEYWORDS = [
            "send money", "urgent", "gift card", "wire transfer", "bitcoin",
            "verify account", "suspended", "click here", "limited time",
            "congratulations", "you won", "claim prize", "inheritance",
            "help me", "emergency", "hospital", "arrested", "bail",
            "irs", "social security", "account frozen", "unusual activity",
        ];

        const financialKeywords = [
            "money", "payment", "transfer", "card", "bank", "account",
            "ssn", "social security", "password", "pin",
        ];

        const urgencyKeywords = [
            "urgent", "immediately", "now", "quick", "hurry", "asap",
            "today", "expires", "limited",
        ];

        let suspiciousScore = 0;
        let reasons = [];

        // Check for scam keywords
        SCAM_KEYWORDS.forEach((keyword) => {
            if (textLower.includes(keyword)) {
                suspiciousScore += 2;
                reasons.push(`Contains: "${keyword}"`);
            }
        });

        // Check for financial + urgency combination
        const hasFinancial = financialKeywords.some(k => textLower.includes(k));
        const hasUrgency = urgencyKeywords.some(k => textLower.includes(k));

        if (hasFinancial && hasUrgency) {
            suspiciousScore += 3;
            reasons.push("Combines financial request with urgency");
        }

        // Check for suspicious links
        if (text.match(/http[s]?:\/\//i) && (
            textLower.includes("bit.ly") ||
            textLower.includes("tinyurl") ||
            text.match(/\.[a-z]{2,3}\/[a-z0-9]{5,}/i) // Shortened URL pattern
        )) {
            suspiciousScore += 2;
            reasons.push("Contains suspicious link");
        }

        return {
            suspicious: suspiciousScore >= 3,
            score: suspiciousScore,
            reasons: reasons,
        };
    }

    /**
     * Analyze message with backend AI
     */
    async function analyzeWithBackend(messageText, senderInfo) {
        try {
            const response = await fetch(`${backendUrl}/api/v1/analyze-message`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: messageText,
                    sender: senderInfo.name,
                    platform: senderInfo.platform,
                    context: {
                        sender_verified: senderInfo.verified,
                    },
                }),
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error("[SENIOR PROTECTION] Backend analysis failed:", error);
            // Fallback to local analysis
            return {
                scam_risk_score: 0.7,
                risk_level: "HIGH",
                senior_friendly_warning: "⚠️ This message seems suspicious. Please be careful and verify before taking any action.",
                recommended_actions: [
                    { action: "verify", label: "Verify First", description: "Check with someone you trust" }
                ],
            };
        }
    }

    /**
     * Add warning overlay to suspicious message
     */
    function addWarningToMessage(messageElement, analysis) {
        // Check if warning already exists
        if (messageElement.querySelector(".senior-protection-warning")) {
            return;
        }

        console.log("[SENIOR PROTECTION] ⚠️  Adding warning to message:", {
            risk: analysis.risk_level,
            score: analysis.scam_risk_score
        });

        const warningDiv = document.createElement("div");
        warningDiv.className = "senior-protection-warning";
        warningDiv.style.cssText = `
      background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
      color: white;
      padding: 16px 20px;
      margin: 12px 0;
      border-radius: 16px;
      font-size: 14px;
      font-weight: 600;
      border: 3px solid #ff5252;
      box-shadow: 0 8px 24px rgba(255, 107, 107, 0.4);
      position: relative;
      z-index: 99999;
      animation: scamAlertPulse 2s infinite;
    `;

        // Add animation
        if (!document.getElementById('scam-alert-animation')) {
            const style = document.createElement('style');
            style.id = 'scam-alert-animation';
            style.textContent = `
                @keyframes scamAlertPulse {
                    0%, 100% { box-shadow: 0 8px 24px rgba(255, 107, 107, 0.4); }
                    50% { box-shadow: 0 8px 32px rgba(255, 107, 107, 0.6); }
                }
            `;
            document.head.appendChild(style);
        }

        const riskEmoji = analysis.risk_level === "CRITICAL" ? "🚨" :
            analysis.risk_level === "HIGH" ? "⚠️" : "⚡";

        warningDiv.innerHTML = `
      <div style="display: flex; align-items: flex-start; gap: 16px;">
        <div style="font-size: 32px; line-height: 1;">${riskEmoji}</div>
        <div style="flex: 1;">
          <div style="font-size: 18px; font-weight: 800; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">
            🛡️ SCAM ALERT - DO NOT RESPOND
          </div>
          <div style="font-size: 14px; opacity: 0.95; margin-bottom: 12px; line-height: 1.5;">
            ${analysis.senior_friendly_warning || 'This message shows signs of a scam. Do not send money or personal information.'}
          </div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button class="senior-protection-details-btn" style="
              background: white;
              color: #ff5252;
              border: none;
              padding: 10px 16px;
              border-radius: 8px;
              font-weight: 700;
              cursor: pointer;
              font-size: 13px;
              box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            ">
              🔍 Why is this a scam?
            </button>
            <button class="senior-protection-report-btn" style="
              background: rgba(255,255,255,0.2);
              color: white;
              border: 2px solid white;
              padding: 10px 16px;
              border-radius: 8px;
              font-weight: 700;
              cursor: pointer;
              font-size: 13px;
            ">
              🚫 Report Scam
            </button>
          </div>
        </div>
      </div>
    `;

        // Find the best place to insert the warning
        let insertTarget = messageElement;

        // Try to find the message container
        const messageContainer = messageElement.closest('[role="row"]') ||
            messageElement.closest('div[data-scope="messages_table"]') ||
            messageElement;

        // Insert warning at the top
        if (messageContainer.parentElement) {
            messageContainer.parentElement.insertBefore(warningDiv, messageContainer);
        } else {
            messageElement.insertBefore(warningDiv, messageElement.firstChild);
        }

        // Add click handlers
        const detailsBtn = warningDiv.querySelector(".senior-protection-details-btn");
        detailsBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            showScamDetails(analysis);
        });

        const reportBtn = warningDiv.querySelector(".senior-protection-report-btn");
        reportBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            window.open('https://www.ftc.gov/complaint', '_blank');
        });

        // Blur the message content for high-risk scams
        if (analysis.risk_level === "CRITICAL" || analysis.risk_level === "HIGH") {
            // Find and blur message text
            const textSelectors = '[dir="auto"], div[style*="text-align"]';
            messageElement.querySelectorAll(textSelectors).forEach((el) => {
                if (!el.closest('.senior-protection-warning')) {
                    el.style.filter = "blur(6px)";
                    el.style.userSelect = "none";
                    el.style.pointerEvents = "none";
                    el.title = "⚠️ Message hidden for your protection - likely a scam";
                }
            });
        }

        // Log success
        console.log("[SENIOR PROTECTION] ✅ Warning added successfully!");
    }

    /**
     * Show detailed scam analysis
     */
    function showScamDetails(analysis) {
        const modal = document.createElement("div");
        modal.className = "senior-protection-modal";
        modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    `;

        modal.innerHTML = `
      <div style="
        background: white;
        border-radius: 16px;
        padding: 24px;
        max-width: 500px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      ">
        <h2 style="margin: 0 0 16px 0; color: #ff5252; font-size: 24px;">
          🛡️ Scam Detection Report
        </h2>
        
        <div style="background: #fff3f3; padding: 16px; border-radius: 12px; margin-bottom: 16px; border-left: 4px solid #ff5252;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px;">
            Risk Level: ${analysis.risk_level}
          </div>
          <div style="font-size: 13px; color: #666; line-height: 1.6;">
            ${analysis.senior_friendly_warning || "This message shows signs of being a scam."}
          </div>
        </div>

        ${analysis.detected_scam_types && analysis.detected_scam_types.length > 0 ? `
          <div style="margin-bottom: 16px;">
            <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #333;">
              Type of Scam:
            </div>
            <div style="background: #f5f5f5; padding: 12px; border-radius: 8px;">
              ${analysis.detected_scam_types.join(", ")}
            </div>
          </div>
        ` : ""}

        <div style="margin-bottom: 16px;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 8px; color: #333;">
            ✅ What You Should Do:
          </div>
          ${(analysis.recommended_actions || []).map((action) => `
            <div style="background: #e8f5e9; padding: 10px 12px; border-radius: 8px; margin-bottom: 8px; font-size: 13px;">
              <strong>${action.label}:</strong> ${action.description}
            </div>
          `).join("")}
        </div>

        <div style="display: flex; gap: 12px; margin-top: 20px;">
          <button onclick="this.closest('.senior-protection-modal').remove()" style="
            flex: 1;
            background: #4caf50;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
          ">
            Got It - I'll Be Careful
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
            font-size: 14px;
          ">
            Learn More About Scams
          </button>
        </div>
      </div>
    `;

        document.body.appendChild(modal);

        // Close on background click
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    /**
     * Log alert for tracking
     */
    function logAlert(messageText, analysis, senderInfo) {
        alertCount++;
        messageScans.push({
            timestamp: new Date().toISOString(),
            sender: senderInfo.name,
            risk_level: analysis.risk_level,
            scam_risk_score: analysis.scam_risk_score,
            message_preview: messageText.substring(0, 100),
        });

        console.log(`[SENIOR PROTECTION] Alert #${alertCount}:`, {
            sender: senderInfo.name,
            risk: analysis.risk_level,
            score: analysis.scam_risk_score,
        });
    }

    /**
     * Send alert to dashboard
     */
    function sendAlertToDashboard(messageText, analysis, senderInfo) {
        // Store in chrome.storage for dashboard
        chrome.storage.local.get(["alerts"], (result) => {
            const alerts = result.alerts || [];
            alerts.unshift({
                id: Date.now(),
                timestamp: new Date().toISOString(),
                type: "message",
                platform: senderInfo.platform,
                sender: senderInfo.name,
                message_preview: messageText.substring(0, 150),
                risk_level: analysis.risk_level,
                scam_risk_score: analysis.scam_risk_score,
                scam_types: analysis.detected_scam_types || [],
            });

            // Keep only last 100 alerts
            if (alerts.length > 100) {
                alerts.length = 100;
            }

            chrome.storage.local.set({ alerts }, () => {
                // Update badge count
                chrome.runtime.sendMessage({
                    action: "updateAlertBadge",
                    count: alerts.filter(a => a.risk_level === "CRITICAL" || a.risk_level === "HIGH").length,
                });
            });
        });
    }

    // Initialize on page load
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

})();

