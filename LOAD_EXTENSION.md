# Load Chrome Extension - Quick Guide

## Backend Status ✅

The backend server is running at: **http://localhost:8000**

Health check: `{"status":"healthy","nim_api_configured":true}`

## Load Extension in Chrome

1. **Open Chrome Extensions Page**

   - Open Chrome browser
   - Navigate to: `chrome://extensions/`
   - OR: Menu (three dots) → Extensions → Manage extensions

2. **Enable Developer Mode**

   - Toggle the "Developer mode" switch in the top-right corner

3. **Load Extension**

   - Click "Load unpacked" button
   - Navigate to: `/Users/nivedithabp/Documents/NvidiaNEMO/extension`
   - Select the `extension` folder and click "Select"

4. **Configure Extension**

   - Click the extension icon in Chrome toolbar
   - Verify backend URL is set to: `http://localhost:8000`
   - Status should show "Connected (NIM API configured)"

5. **Test on YouTube**
   - Navigate to any YouTube video
   - Click the "Analyze Video" button below the player
   - Watch analysis results appear in real-time!

## Quick Commands

**Stop Backend:**

```bash
lsof -ti:8000 | xargs kill
```

**Restart Backend:**

```bash
cd /Users/nivedithabp/Documents/NvidiaNEMO/backend
python3 main.py
```

## Troubleshooting

- **Extension not loading**: Make sure you selected the `extension` folder (not a parent folder)
- **Connection failed**: Verify backend is running (`curl http://localhost:8000/api/v1/health`)
- **Icons missing**: Extension will work without icons, Chrome shows default icon
