/**
 * "Is this video real?" on YouTube and Facebook.
 *
 * The previous build tried seven different DOM insertion strategies to place
 * its button inside the host page's layout, and logged whether each worked.
 * It moved between page types and sometimes vanished. This uses one fixed
 * position: the button is in the same place on every page, every time, which
 * matters more for a 78-year-old than blending into YouTube's chrome.
 */

(function () {
  "use strict";

  const RUAI = window.RUAI;
  const el = RUAI.el;

  const LAUNCHER_ID = "ruai-video-launcher";

  const platform = location.hostname.includes("youtube.com")
    ? "youtube"
    : location.hostname.includes("facebook.com")
      ? "facebook"
      : "web";

  let launcher = null;
  let label = null;
  let pill = null;
  let checking = false;
  // Bumped whenever a check is abandoned, so a late reply from a cancelled
  // run cannot pop a sheet the user has already dismissed.
  let runId = 0;

  // --- Setup ------------------------------------------------------------

  async function init() {
    const settings = await RUAI.settings.get();
    if (!settings.videoChecksEnabled) return;
    if (document.getElementById(LAUNCHER_ID)) return;
    if (!(await waitForVideo())) return;

    mount();
  }

  function waitForVideo(timeoutMs = 15000) {
    return new Promise((resolve) => {
      if (document.querySelector("video")) return resolve(true);

      const deadline = Date.now() + timeoutMs;
      const observer = new MutationObserver(() => {
        if (document.querySelector("video")) {
          observer.disconnect();
          resolve(true);
        } else if (Date.now() > deadline) {
          observer.disconnect();
          resolve(false);
        }
      });
      observer.observe(document.documentElement, { childList: true, subtree: true });
      setTimeout(() => {
        observer.disconnect();
        resolve(Boolean(document.querySelector("video")));
      }, timeoutMs);
    });
  }

  function mount() {
    label = el("span", { text: "Is this video real?" });
    pill = el("span", { class: "ruai-visually-hidden" });

    const button = el(
      "button",
      {
        type: "button",
        class: "ruai-launcher-btn",
        "data-state": "idle",
        on: { click: runCheck },
      },
      [RUAI.view.mark(28), label, pill]
    );

    launcher = el("div", { id: LAUNCHER_ID, class: "ruai-root ruai-launcher" }, [button]);
    document.body.append(launcher);
  }

  function teardown() {
    runId += 1;
    RUAI.view.closeSheet();
    document.getElementById(LAUNCHER_ID)?.remove();
    launcher = null;
    checking = false;
  }

  function setState(state, text) {
    const button = launcher?.querySelector(".ruai-launcher-btn");
    if (!button) return;
    button.dataset.state = state;
    button.disabled = state === "working";
    if (text) label.textContent = text;
  }

  function showResultPill(risk) {
    pill.className = "ruai-pill";
    pill.dataset.risk = risk;
    pill.textContent = RUAI.RISK_LABEL[risk] || "Checked";
  }

  // --- Capture ----------------------------------------------------------

  function captureFrame(video) {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    if (!canvas.width || !canvas.height) return null;

    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    // Throws SecurityError if the page served the video cross-origin without
    // CORS, which taints the canvas. Callers translate that into plain words.
    return canvas.toDataURL("image/jpeg", 0.82).split(",")[1];
  }

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  /**
   * Grab a short burst while the video plays. A paused video yields one
   * frame, which still catches melted hands and garbled signage.
   */
  async function captureBurst(video) {
    const frames = [];
    const wanted = video.paused ? 1 : RUAI.FRAME_BURST;

    for (let index = 0; index < wanted; index += 1) {
      const image = captureFrame(video);
      if (image) frames.push({ image, timestamp: video.currentTime });
      if (index < wanted - 1) await wait(RUAI.FRAME_GAP_MS);
    }
    return frames;
  }

  // --- Page metadata ----------------------------------------------------

  function videoMetadata() {
    if (platform === "youtube") {
      const params = new URLSearchParams(location.search);
      const heading = document.querySelector(
        "h1.ytd-watch-metadata yt-formatted-string, h1.title yt-formatted-string, h1 .ytd-reel-player-header-renderer"
      );
      return {
        video_id: params.get("v") || location.pathname.split("/").filter(Boolean).pop() || null,
        title: heading?.textContent.trim() || document.title.replace(/ - YouTube$/, "") || null,
      };
    }

    const selectors = ['[data-ad-comet-preview="message"]', '[role="main"] h2', 'h2[dir="auto"]'];
    let title = null;
    for (const selector of selectors) {
      const node = document.querySelector(selector);
      if (node?.textContent.trim()) {
        title = node.textContent.trim();
        break;
      }
    }
    return {
      video_id: location.pathname.split("/").filter(Boolean).pop() || null,
      title: title || document.title.split("|")[0].trim() || null,
    };
  }

  // --- The check --------------------------------------------------------

  async function runCheck() {
    if (checking) return;

    const video = document.querySelector("video");
    if (!video) {
      RUAI.view.showSheet(
        RUAI.view.messageCard(
          "No video found on this page",
          "Open a video and try again."
        )
      );
      return;
    }

    if (!video.videoWidth) {
      RUAI.view.showSheet(
        RUAI.view.messageCard(
          "The video has not started yet",
          "Press play, let it run for a second, then check again."
        )
      );
      return;
    }

    checking = true;
    runId += 1;
    const thisRun = runId;
    const abandoned = () => thisRun !== runId;

    setState("working", "Checking…");

    RUAI.view.showSheet(
      RUAI.view.workingCard(
        "Looking at this video",
        "This usually takes a few seconds."
      ),
      {
        actions: [
          {
            label: "Cancel",
            primary: false,
            // The request cannot be recalled, but its answer can be ignored.
            onClick: () => {
              runId += 1;
              setState("idle", "Is this video real?");
            },
          },
        ],
      }
    );

    try {
      const frames = await captureBurst(video);
      if (!frames.length) throw new RUAI.RuaiError("RUAI could not read this video.");

      const meta = videoMetadata();
      const verdict = await RUAI.api.checkVideo({
        frames,
        title: meta.title,
        video_id: meta.video_id,
        platform,
      });

      if (abandoned()) return;

      showResultPill(verdict.risk);
      setState("idle", "Check again");
      present(verdict);
    } catch (error) {
      console.warn("[RUAI] video check failed:", error);
      if (abandoned()) return;

      const message =
        error?.name === "SecurityError"
          ? "This site does not let RUAI read the video picture."
          : error?.userMessage || "Something went wrong. Please try again.";

      setState("idle", "Try again");
      RUAI.view.showSheet(RUAI.view.messageCard("RUAI could not check this", message));
    } finally {
      checking = false;
    }
  }

  function present(verdict) {
    RUAI.view.showSheet(RUAI.view.verdictCard(verdict), {
      label: "Video check result",
      actions: [
        { label: "Close", primary: true },
        { label: "Check again", primary: false, onClick: () => setTimeout(runCheck, 60) },
      ],
    });
  }

  // --- Single-page navigation -------------------------------------------

  let lastUrl = location.href;
  new MutationObserver(() => {
    if (location.href === lastUrl) return;
    lastUrl = location.href;
    teardown();
    setTimeout(init, 800);
  }).observe(document, { subtree: true, childList: true });

  init();
})();
