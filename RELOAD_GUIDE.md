# Quick Reload Guide

## 🔄 Reload Chrome Extension

### Method 1: From Extensions Page

1. Open Chrome and go to `chrome://extensions/`
2. Find "AI Video Fakeness Detector" extension
3. Click the **🔄 Reload** icon (circular arrow) next to the extension
4. Refresh the YouTube page you're testing on (F5 or Cmd+R)

### Method 2: Developer Mode Quick Reload

1. Go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click the reload button on your extension
4. Extension will reload and pick up all code changes

### What Gets Reloaded:

- ✅ `content.js` - Script that runs on YouTube pages
- ✅ `background.js` - Service worker
- ✅ `popup.html/js/css` - Extension popup UI
- ✅ `manifest.json` - Extension configuration
- ✅ `content.css` - Styles for injected UI

**Note:** After reloading, refresh any YouTube pages you have open to see changes.

---

## 🔄 Restart Backend Server

### Method 1: Stop and Restart (Current Session)

The backend is currently running. To restart:

1. **Stop the current server:**

   ```bash
   # Find the process ID
   lsof -ti:8000

   # Kill it
   lsof -ti:8000 | xargs kill
   ```

2. **Restart:**
   ```bash
   cd /Users/nivedithabp/Documents/NvidiaNEMO/backend
   python3 main.py
   ```

### Method 2: Use Auto-Reload (Already Enabled)

The backend is running with `--reload` flag, so it **automatically reloads** when you change Python files!

**Just save your `.py` files and the server will reload automatically.**

You'll see messages like:

```
INFO: Detected file change in 'path/to/file.py'. Reloading...
```

### Method 3: Manual Restart Script

Create a restart script for convenience:

```bash
# Save as restart_backend.sh
#!/bin/bash
cd /Users/nivedithabp/Documents/NvidiaNEMO/backend
lsof -ti:8000 | xargs kill 2>/dev/null
sleep 1
python3 main.py
```

Then run: `bash restart_backend.sh`

---

## 🧪 Test After Reload

### Test Extension:

1. Go to any YouTube video: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. Check browser console (F12) for logs
3. Look for the "Analyze Video" button

### Test Backend:

```bash
curl http://localhost:8000/api/v1/health
```

Should return: `{"status":"healthy","nim_api_configured":true}`

---

## 🔍 Debug Tips

### Check Extension Logs:

1. Open YouTube page
2. Press F12 → Console tab
3. Look for: "AI Video Fakeness Detector initialized"

### Check Backend Logs:

The terminal running the backend shows all requests:

```
INFO:     127.0.0.1:xxxxx - "GET /api/v1/health HTTP/1.1" 200 OK
```

### Verify Extension is Loaded:

1. Go to `chrome://extensions/`
2. Ensure extension status is "Enabled" (not "Error")
3. Check for any red error messages

---

## ⚡ Quick Reload Commands

**Reload Extension:** Just click reload icon in `chrome://extensions/`

**Restart Backend:**

```bash
cd /Users/nivedithabp/Documents/NvidiaNEMO/backend
lsof -ti:8000 | xargs kill && python3 main.py
```

**View Backend Logs:** Check the terminal where you ran `python3 main.py`

---

## 🐛 Common Issues

**Extension not updating:**

- Hard refresh YouTube page (Cmd+Shift+R or Ctrl+Shift+R)
- Completely close and reopen Chrome
- Check for errors in `chrome://extensions/`

**Backend not restarting:**

- Make sure port 8000 is free: `lsof -ti:8000`
- Check for syntax errors in Python files
- Verify `.env` file exists and has valid API key
