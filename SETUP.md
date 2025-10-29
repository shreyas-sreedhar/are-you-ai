# Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your NVIDIA NIM API key
uvicorn main:app --reload --port 8000
```

### 2. Extension Setup

1. Open Chrome → Extensions (`chrome://extensions/`)
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder
5. Configure backend URL in extension popup

### 3. Get NVIDIA NIM API Key

1. Sign up at [NVIDIA NIM API](https://build.nvidia.com/)
2. Get your API key from the dashboard
3. Add it to `backend/.env` as `NIM_API_KEY`

### 4. Create Extension Icons

You'll need to create three icon files in `extension/icons/`:

- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

You can use any image editor or online icon generator. For now, the extension will work without icons (Chrome will show a default icon).

## Testing

### Test Backend

```bash
curl http://localhost:8000/api/v1/health
```

### Test Extension

1. Navigate to any YouTube video
2. Click "Analyze Video" button
3. Wait for analysis results

## Troubleshooting

- **Backend won't start**: Check that port 8000 is available and Python dependencies are installed
- **Extension can't connect**: Verify backend URL in extension popup settings
- **Analysis fails**: Check NIM API key and network connection
- **No icons showing**: Create icon files or extension will use default Chrome icons
