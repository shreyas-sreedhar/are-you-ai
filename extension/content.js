/**
 * Content script for YouTube video page
 * Handles frame extraction and UI injection
 */

(function () {
  "use strict";

  // Constants
  const FRAME_EXTRACTION_INTERVAL = 5000; // 5 seconds
  let extractionInterval = null;
  let currentAnalysisState = null;
  let backendUrl = "http://localhost:8000";

  // Initialize extension
  console.log("[AIVFD] Starting initialization...");
  init().catch(error => {
    console.error("[AIVFD] Initialization error:", error);
    // Try to inject UI anyway after a delay
    setTimeout(() => {
      try {
        console.log("[AIVFD] Attempting fallback UI injection...");
        injectUI();
        console.log("[AIVFD] UI injected (fallback)");
      } catch (e) {
        console.error("[AIVFD] Failed to inject UI:", e);
      }
    }, 2000);
  });

  /**
   * Initialize the extension on YouTube page
   */
  async function init() {
    try {
      // Get backend URL from storage
      backendUrl = await getBackendUrl();

      // Wait for YouTube player to be available (but don't fail if it takes too long)
      try {
        await waitForPlayer();
      } catch (e) {
        console.warn("Player not ready yet, will inject UI anyway:", e);
      }

      // Inject UI into YouTube page
      console.log("[AIVFD] Injecting UI...");
      injectUI();

      console.log("[AIVFD] AI Video Fakeness Detector initialized successfully");
    } catch (error) {
      console.error("Error in init:", error);
      throw error;
    }
  }

  /**
   * Get backend URL from extension storage
   */
  async function getBackendUrl() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: "getBackendUrl" }, (response) => {
        resolve(response?.backendUrl || "http://localhost:8000");
      });
    });
  }

  /**
   * Wait for YouTube video player to be available
   */
  async function waitForPlayer() {
    const maxAttempts = 100; // Increased attempts
    let attempts = 0;

    while (attempts < maxAttempts) {
      const video = document.querySelector("video");
      if (video) {
        // Don't require readyState, just check if video element exists
        return video;
      }
      await new Promise((resolve) => setTimeout(resolve, 100));
      attempts++;
    }
    throw new Error("Video player not found after waiting");
  }

  /**
   * Inject UI controls into YouTube page
   */
  function injectUI() {
    // Check if UI already exists
    if (document.getElementById("aivfd-container")) {
      console.log("AI Video Fakeness Detector UI already exists");
      return;
    }

    console.log("[AIVFD] Injecting AI Video Fakeness Detector UI...");

    const container = document.createElement("div");
    container.id = "aivfd-container";
    container.innerHTML = `
      <div id="aivfd-controls">
        <div class="aivfd-pill-group" id="aivfd-ctrl-pills">
          <span id="aivfd-analyze-btn" class="aivfd-pill aivfd-pill-btn">Start</span>
          <span id="aivfd-stop-btn" class="aivfd-pill aivfd-pill-btn" style="display:none;">Stop</span>
        </div>
      </div>
      <div id="aivfd-results" style="display: none;"></div>
    `;

    // Try multiple strategies to insert the UI
    let inserted = false;
    const isShorts = window.location.pathname.includes('/shorts/');
    
    // Strategy 1: For Shorts, ALWAYS use fixed positioning for visibility
    if (isShorts) {
      // For Shorts, position container without a box background
      container.style.cssText = `
        position: fixed !important;
        top: 120px !important;
        right: 20px !important;
        z-index: 999999 !important;
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        min-width: unset !important;
      `;
      document.body.appendChild(container);
      inserted = true;
      console.log("[AIVFD] UI inserted with fixed positioning for Shorts page");
    }
    
    // Strategy 2: Try to insert after YouTube player container (regular videos)
    if (!inserted) {
      const playerContainer = document.querySelector("#movie_player") || document.querySelector("#player");
      if (playerContainer && playerContainer.parentElement) {
        try {
          playerContainer.parentElement.insertBefore(container, playerContainer.nextSibling);
          inserted = true;
          console.log("UI inserted after player container");
        } catch (e) {
          console.warn("Failed to insert after player:", e);
        }
      }
    }
    
    // Strategy 3: Try to insert after video element
    if (!inserted) {
      const video = document.querySelector("video");
      if (video && video.parentElement) {
        try {
          video.parentElement.insertBefore(container, video.nextSibling);
          inserted = true;
          console.log("UI inserted after video element");
        } catch (e) {
          console.warn("Failed to insert after video:", e);
        }
      }
    }
    
    // Strategy 4: Try to find secondary-guide-inner container (common YouTube structure)
    if (!inserted) {
      const secondaryInner = document.querySelector("#secondary-inner");
      if (secondaryInner) {
        try {
          secondaryInner.insertBefore(container, secondaryInner.firstChild);
          inserted = true;
          console.log("UI inserted in secondary-inner");
        } catch (e) {
          console.warn("Failed to insert in secondary-inner:", e);
        }
      }
    }
    
    // Strategy 5: Try to find #secondary (YouTube sidebar area)
    if (!inserted) {
      const secondary = document.querySelector("#secondary");
      if (secondary) {
        try {
          secondary.insertBefore(container, secondary.firstChild);
          inserted = true;
          console.log("UI inserted in secondary");
        } catch (e) {
          console.warn("Failed to insert in secondary:", e);
        }
      }
    }
    
    // Strategy 6: Fallback - append to body (fixed position will make it visible)
    if (!inserted) {
      // Ensure visibility without any white box background
      container.style.cssText = `
        position: fixed !important;
        top: 100px !important;
        right: 20px !important;
        z-index: 999999 !important;
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        min-width: unset !important;
      `;
      document.body.appendChild(container);
      console.log("[AIVFD] UI appended to body with fixed positioning (fallback) - should be visible top-right");
    }
    
    // Verify button was created and is visible
    const button = document.getElementById("aivfd-analyze-btn");
    if (button) {
      console.log("[AIVFD] ✅ Analyze button found and ready!");
      
      // Check if button is actually visible
      const rect = button.getBoundingClientRect();
      const isVisible = rect.width > 0 && rect.height > 0 && 
                       window.getComputedStyle(button).display !== 'none' &&
                       window.getComputedStyle(button).visibility !== 'hidden';
      
      if (!isVisible) {
        console.warn("[AIVFD] ⚠️ Button exists but may not be visible!", {
          width: rect.width,
          height: rect.height,
          display: window.getComputedStyle(button).display,
          visibility: window.getComputedStyle(button).visibility
        });
        
        // Force visibility
        button.style.display = "inline-flex";
        button.style.visibility = "visible";
        button.style.opacity = "1";
      } else {
        console.log("[AIVFD] ✅ Button is visible at position:", {
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height
        });
      }
    } else {
      console.error("[AIVFD] ❌ Analyze button NOT found after injection!");
    }

    // Attach event listeners with error handling
    try {
      const analyzeBtn = document.getElementById("aivfd-analyze-btn");
      const stopBtn = document.getElementById("aivfd-stop-btn");
      
      if (analyzeBtn) {
        // Add multiple event listeners to ensure it works
        analyzeBtn.addEventListener("click", (e) => {
          console.log("[AIVFD] 🔴 Analyze button CLICKED!");
          e.preventDefault();
          e.stopPropagation();
          startAnalysis();
        }, true); // Use capture phase
        
        // Also add mousedown as backup
        analyzeBtn.addEventListener("mousedown", (e) => {
          console.log("[AIVFD] Analyze button mousedown event");
        });
        
        console.log("[AIVFD] Analyze button event listeners attached");
      } else {
        console.error("[AIVFD] Analyze button not found!");
      }
      
      if (stopBtn) {
        stopBtn.addEventListener("click", stopAnalysis);
        console.log("Stop button event listener attached");
      }
    } catch (e) {
      console.error("Error attaching event listeners:", e);
    }
  }

  /**
   * Start frame extraction and analysis
   */
  async function startAnalysis() {
    try {
      // Check backend health
      const isHealthy = await checkBackendHealth();
      if (!isHealthy) {
        showError("Backend API is not accessible. Please check your settings.");
        return;
      }

      // Update UI (toggle to Stop and show loading indicator in badge group)
      setAnalyzingUI(true);

      // Get video metadata
      const videoData = getVideoMetadata();
      currentAnalysisState = {
        videoId: videoData.videoId,
        videoTitle: videoData.title,
        frames: [],
        startTime: Date.now(),
      };

      // Start extracting frames at intervals
      extractionInterval = setInterval(async () => {
        await extractAndAnalyzeFrame();
      }, FRAME_EXTRACTION_INTERVAL);

      // Analyze first frame immediately
      await extractAndAnalyzeFrame();

    } catch (error) {
      console.error("Error starting analysis:", error);
      showError(`Failed to start analysis: ${error.message}`);
    }
  }

  /**
   * Stop frame extraction
   */
  function stopAnalysis() {
    if (extractionInterval) {
      clearInterval(extractionInterval);
      extractionInterval = null;
    }

    setAnalyzingUI(false);

    // Do not render the large summary card; Details overlay is the source of truth
    const resultsDiv = document.getElementById("aivfd-results");
    if (resultsDiv) {
      resultsDiv.innerHTML = "";
      resultsDiv.style.display = "none";
    }
  }

  function setAnalyzingUI(isAnalyzing) {
    const startBtn = document.getElementById("aivfd-analyze-btn");
    const stopBtn = document.getElementById("aivfd-stop-btn");
    if (!startBtn || !stopBtn) return;
    if (isAnalyzing) {
      startBtn.style.display = "none";
      stopBtn.style.display = "inline-flex";
      // switch refresh to spinner
      const refresh = document.getElementById("aivfd-refresh-btn");
      if (refresh) refresh.innerHTML = `<span class="aivfd-spinner"></span>Analyzing`;
    } else {
      startBtn.style.display = "inline-flex";
      stopBtn.style.display = "none";
      const refresh = document.getElementById("aivfd-refresh-btn");
      if (refresh) refresh.textContent = "Refresh";
    }
  }

  /**
   * Extract current frame from video and analyze
   */
  async function extractAndAnalyzeFrame() {
    try {
      const video = document.querySelector("video");
      if (!video || video.paused) {
        return;
      }

      // Get current timestamp
      const timestamp = video.currentTime;

      // Extract frame using canvas
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to base64
      const base64Frame = canvas.toDataURL("image/jpeg", 0.85).split(",")[1];

      // Send to backend for analysis
      const result = await analyzeFrame(base64Frame, timestamp);

      // Store result
      currentAnalysisState.frames.push({
        timestamp,
        result
      });

      // Update UI with latest result
      updateResultsUI(result);

    } catch (error) {
      console.error("Error extracting/analyzing frame:", error);
    }
  }

  /**
   * Send frame to backend for analysis
   */
  async function analyzeFrame(base64Frame, timestamp) {
    const videoData = getVideoMetadata();
    
    const response = await fetch(`${backendUrl}/api/v1/analyze-frame`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        frame: base64Frame,
        video_id: videoData.videoId,
        timestamp: timestamp,
        video_title: videoData.title,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Update results UI with latest analysis
   */
  function updateResultsUI(result) {
    const isFake = result.is_likely_fake === true;
    const badgeText = isFake ? "AI" : "REAL";

    // Create or update badge container
    let badgeContainer = document.getElementById("aivfd-badge-container");
    if (!badgeContainer) {
      badgeContainer = document.createElement("div");
      badgeContainer.id = "aivfd-badge-container";
      badgeContainer.className = "aivfd-badge-container";
      badgeContainer.innerHTML = `
        <div class="aivfd-pill-group">
          <span id="aivfd-badge" class="aivfd-pill is-badge">...</span>
          <span id="aivfd-refresh-btn" class="aivfd-pill aivfd-pill-btn">Refresh</span>
          <span id="aivfd-details-btn" class="aivfd-pill aivfd-pill-btn">Details</span>
        </div>
      `;
      document.body.appendChild(badgeContainer);
      // Refresh click handler
      document.getElementById("aivfd-refresh-btn").addEventListener("click", () => refreshAnalysis());
      // Details click handler
      document.getElementById("aivfd-details-btn").addEventListener("click", () => showDetailsOverlay(result));
    }

    const badge = document.getElementById("aivfd-badge");
    badge.className = `aivfd-pill is-badge ${isFake ? "aivfd-pill-ai" : "aivfd-pill-real"}`;
    badge.textContent = badgeText;

    // Hide the large results card; only show on Details overlay
    document.getElementById("aivfd-results").style.display = "none";
  }

  function clearBadgeAndOverlay() {
    const badge = document.getElementById("aivfd-badge-container");
    if (badge && badge.parentNode) badge.parentNode.removeChild(badge);
    const overlay = document.getElementById("aivfd-overlay");
    if (overlay) overlay.classList.remove("open");
  }

  async function refreshAnalysis() {
    try {
      const video = document.querySelector("video");
      if (!video) return;
      // Pause current interval and run a single fresh analysis
      if (extractionInterval) {
        clearInterval(extractionInterval);
        extractionInterval = null;
      }
      currentAnalysisState.frames = [];
      await extractAndAnalyzeFrame();
      // Resume interval
      extractionInterval = setInterval(async () => {
        await extractAndAnalyzeFrame();
      }, FRAME_EXTRACTION_INTERVAL);
    } catch (e) {
      console.error("[AIVFD] Refresh failed:", e);
    }
  }

  // Transparent overlay for details
  function ensureOverlay() {
    let overlay = document.getElementById("aivfd-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "aivfd-overlay";
      overlay.className = "aivfd-overlay";
      overlay.innerHTML = `<div class="aivfd-overlay-panel" id="aivfd-overlay-panel"></div>`;
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) overlay.classList.remove("open");
      });
      document.body.appendChild(overlay);
    }
    return overlay;
  }

  function showDetailsOverlay(result) {
    const overlay = ensureOverlay();
    const panel = document.getElementById("aivfd-overlay-panel");

    const confidence = (result.confidence_score * 100).toFixed(1);
    const isFake = result.is_likely_fake === true;
    const inconsistencyCount = result.inconsistencies?.length || 0;

    const detailsHtml = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <div style="font-size:16px;font-weight:700;">Analysis Details</div>
        <button id="aivfd-overlay-close" class="aivfd-details-btn">Close</button>
      </div>
      <div style="display:flex;gap:12px;align-items:center;margin-bottom:12px;">
        <span class="aivfd-badge ${isFake ? "aivfd-badge-ai" : "aivfd-badge-real"}">${isFake ? "AI" : "REAL"}</span>
        <div style="font-weight:600;">Confidence: ${confidence}%</div>
        <div>Issues: ${inconsistencyCount}</div>
      </div>
      ${inconsistencyCount > 0 ? `
        <div class="aivfd-inconsistencies">
          <h4>Detected Issues</h4>
          <ul>
            ${result.inconsistencies.map(inc => `
              <li>
                <span class="aivfd-severity aivfd-severity-${inc.severity}">${inc.severity}</span>
                ${inc.type}: ${inc.description}
                ${inc.location ? ` (${inc.location})` : ""}
              </li>
            `).join("")}
          </ul>
        </div>
      ` : "<div>No significant inconsistencies detected.</div>"}
      <div class="aivfd-reasoning" style="margin-top:10px;">
        <details open>
          <summary>Reasoning</summary>
          <p>${result.reasoning || "No detailed reasoning available."}</p>
        </details>
      </div>
    `;

    panel.innerHTML = detailsHtml;
    overlay.classList.add("open");
    document.getElementById("aivfd-overlay-close").addEventListener("click", () => overlay.classList.remove("open"));
  }

  /**
   * Display final batch analysis results
   */
  async function displayFinalResults() {
    try {
      showResults(`<div class="aivfd-loading">Computing final analysis...</div>`);

      // Send batch to backend
      const frames = currentAnalysisState.frames.map((f) => ({
        frame: f.result.frame || "", // Note: we'd need to store the frame data
        timestamp: f.timestamp,
        video_id: currentAnalysisState.videoId,
        video_title: currentAnalysisState.videoTitle,
      }));

      // For now, compute summary from existing results
      const fakeCount = currentAnalysisState.frames.filter((f) => f.result.is_likely_fake).length;
      const avgConfidence = currentAnalysisState.frames.reduce((sum, f) => sum + f.result.confidence_score, 0) / currentAnalysisState.frames.length;

      const html = `
        <div class="aivfd-result-card">
          <div class="aivfd-header">
            <h3>Final Analysis Summary</h3>
          </div>
          <div class="aivfd-stats">
            <div class="aivfd-stat">
              <span class="aivfd-stat-label">Total Frames:</span>
              <span class="aivfd-stat-value">${currentAnalysisState.frames.length}</span>
            </div>
            <div class="aivfd-stat">
              <span class="aivfd-stat-label">Average Confidence:</span>
              <span class="aivfd-stat-value">${(avgConfidence * 100).toFixed(1)}%</span>
            </div>
            <div class="aivfd-stat">
              <span class="aivfd-stat-label">Suspicious Frames:</span>
              <span class="aivfd-stat-value">${fakeCount} (${((fakeCount / currentAnalysisState.frames.length) * 100).toFixed(1)}%)</span>
            </div>
          </div>
        </div>
      `;

      showResults(html);

    } catch (error) {
      console.error("Error displaying final results:", error);
      showError(`Failed to compute final results: ${error.message}`);
    }
  }

  /**
   * Get video metadata from YouTube page
   */
  function getVideoMetadata() {
    const videoId = new URLSearchParams(window.location.search).get("v");
    const titleElement = document.querySelector('h1.ytd-watch-metadata yt-formatted-string, h1.title yt-formatted-string');
    const title = titleElement ? titleElement.textContent.trim() : "Unknown Video";

    return {
      videoId,
      title,
    };
  }

  /**
   * Check backend health
   */
  async function checkBackendHealth() {
    try {
      const response = await fetch(`${backendUrl}/api/v1/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  /**
   * Show results in UI
   */
  function showResults(html) {
    const resultsDiv = document.getElementById("aivfd-results");
    resultsDiv.innerHTML = html;
    resultsDiv.style.display = "block";
  }

  /**
   * Show error message
   */
  function showError(message) {
    showResults(`<div class="aivfd-error">${message}</div>`);
  }

  // Listen for YouTube navigation (SPA)
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      // Reset UI and re-initialize on navigation
      try {
        stopAnalysis();
      } catch {}
      clearBadgeAndOverlay();
      setTimeout(init, 1000);
    }
  }).observe(document, { subtree: true, childList: true });

})();

