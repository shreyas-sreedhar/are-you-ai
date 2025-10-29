# Facebook Reels Support Guide

## Changes Made

Your AI Video Detector extension now supports **Facebook Reels** in addition to YouTube videos! 

### What's New:
1. ✅ Facebook Reels detection and analysis
2. ✅ Multi-platform video metadata extraction
3. ✅ Adaptive UI positioning for Facebook's layout
4. ✅ Real-time frame analysis for Facebook videos

## How to Reload the Extension

After making changes to the extension, you need to reload it in Chrome:

### Step 1: Open Chrome Extensions Page
1. Open Chrome/Edge browser
2. Navigate to `chrome://extensions/` (or `edge://extensions/`)
3. Make sure **Developer mode** is enabled (toggle in top-right)

### Step 2: Reload the Extension
1. Find "AI Video Fakeness Detector" in the list
2. Click the **Reload** button (circular arrow icon)
3. Verify the extension is enabled (toggle switch should be ON)

### Step 3: Hard Refresh Any Open Tabs
- If you already have Facebook or YouTube open:
  - Press `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows/Linux)
  - Or close and reopen the tabs

## Testing with Facebook Reels

### Step 1: Navigate to a Facebook Reel
Go to Facebook and find a Reel video. URLs look like:
- `https://www.facebook.com/reel/123456789`
- `https://www.facebook.com/username/videos/123456789`
- `https://www.facebook.com/watch?v=123456789`

### Step 2: Look for the "Start" Button
The extension will inject a **"Start" button** in the top-right area of the page (similar to YouTube).

If you don't see it:
1. Open Chrome DevTools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Look for `[AIVFD]` log messages
4. Check if there are any errors

### Step 3: Start Analysis
1. Make sure the video is playing
2. Click the **"Start"** button
3. The extension will:
   - Extract frames every 5 seconds
   - Send them to your backend API
   - Analyze with NVIDIA Nemotron-nano-12b-v2-vl model
   - Show results in a badge (AI/REAL)

### Step 4: View Results
- A badge will appear showing **"AI"** or **"REAL"**
- Click **"Details"** to see:
  - Confidence score
  - Detected inconsistencies
  - AI reasoning

## Troubleshooting

### Button Not Showing?

**Check Console Logs:**
1. Open DevTools (F12)
2. Go to Console tab
3. Look for these messages:
   ```
   [AIVFD] Starting initialization on facebook...
   [AIVFD] Video element found on facebook
   [AIVFD] Injecting UI...
   [AIVFD] ✅ Analyze button found and ready!
   ```

**Common Issues:**

1. **Video element not found**
   - Wait for the page to fully load
   - Scroll to ensure the video is visible
   - Refresh the page (Cmd+Shift+R)

2. **Button exists but not visible**
   - The extension uses fixed positioning (top: 100-120px, right: 20px)
   - Try zooming out (Cmd+-)
   - Check if any Facebook UI is overlapping

3. **Backend not configured**
   - Make sure your backend is running on `http://localhost:8000`
   - Check the extension popup to verify API URL
   - Test the health endpoint: `http://localhost:8000/api/v1/health`

### Video Not Analyzing?

1. **Ensure video is playing**
   - The extension only extracts frames while video is playing
   - If video is paused, it won't capture frames

2. **Check backend logs**
   - Look at your Python backend terminal
   - Ensure NVIDIA NIM API key is configured
   - Check for any API errors

3. **Network errors**
   - Open DevTools → Network tab
   - Look for failed requests to `/api/v1/analyze-frame`
   - Verify CORS is not blocking requests

## Supported Platforms

✅ **YouTube**
- Regular videos (`/watch?v=...`)
- YouTube Shorts (`/shorts/...`)

✅ **Facebook** (NEW!)
- Facebook Reels (`/reel/...`)
- Video posts (`/username/videos/...`)
- Watch videos (`/watch?v=...`)

## Technical Details

### How It Works:

1. **Platform Detection**: Automatically detects if you're on YouTube or Facebook
2. **Video Element**: Finds the HTML5 `<video>` element on the page
3. **Frame Extraction**: Uses Canvas API to capture frames every 5 seconds
4. **Analysis**: Sends base64-encoded frames to your backend
5. **NVIDIA NIM**: Backend uses Nemotron-nano-12b-v2-vl model for vision analysis
6. **Results Display**: Shows confidence score and detected anomalies

### Files Modified:
- `extension/manifest.json` - Added Facebook permissions and content script matches
- `extension/content.js` - Added multi-platform support with Facebook-specific DOM handling

## Next Steps

1. **Test on various Facebook Reels** to ensure compatibility
2. **Check different types of videos** (real vs AI-generated)
3. **Monitor performance** and frame extraction accuracy
4. **Report any issues** with specific Facebook video formats

## Demo Flow

```
1. Start backend: cd backend && python main.py
2. Reload extension in chrome://extensions/
3. Go to Facebook Reel
4. Wait for "Start" button to appear
5. Click "Start"
6. Watch the magic! 🎭
```

---

**Need Help?** Check the console logs for `[AIVFD]` messages to debug any issues.

