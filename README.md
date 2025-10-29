# AI Video Fakeness Detector

A Chrome browser extension that detects AI-generated fake videos on YouTube by analyzing video frames for visual inconsistencies using NVIDIA's Nemotron-nano-12b-v2-vl model deployed via NIM API.

## Architecture

- **Frontend**: Chrome Extension (JavaScript) - captures frames from YouTube videos
- **Backend**: Python FastAPI server - analyzes frames using NVIDIA NIM API

## Project Structure

```
.
├── backend/                  # Python FastAPI backend
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example        # Environment variables template
│   ├── config/             # Configuration
│   ├── services/           # Business logic (NIM client, frame analyzer)
│   ├── api/                # API routes and models
│   └── utils/              # Utility functions
│
└── extension/               # Chrome Extension
    ├── manifest.json       # Extension manifest (V3)
    ├── background.js       # Service worker
    ├── content.js          # YouTube page injection
    ├── content.css         # Extension styles
    ├── popup/              # Extension popup UI
    └── icons/              # Extension icons (placeholder)
```

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
# Edit .env and add your NVIDIA NIM API key
```

4. Run the server:

```bash
uvicorn main:app --reload --port 8000
```

Or using Python:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`

2. Enable "Developer mode" (toggle in top right)

3. Click "Load unpacked" and select the `extension` folder

4. Click the extension icon and configure the backend API URL (default: `http://localhost:8000`)

5. Navigate to any YouTube video and click "Analyze Video"

## Usage

1. **Configure Backend**: Open the extension popup and set your backend API URL

2. **Navigate to YouTube**: Go to any YouTube video page

3. **Start Analysis**: Click the "Analyze Video" button that appears below the video player

4. **View Results**: Analysis results will be displayed in real-time, showing:

   - Confidence score (percentage)
   - Whether the video is likely AI-generated
   - Detected inconsistencies and artifacts
   - Detailed reasoning

5. **Stop Analysis**: Click "Stop Analysis" to halt frame extraction (results summary will be shown)

## API Endpoints

### Health Check

```
GET /api/v1/health
```

### Analyze Single Frame

```
POST /api/v1/analyze-frame
Body:
{
  "frame": "base64_encoded_image",
  "video_id": "optional_youtube_id",
  "timestamp": 123.45,
  "video_title": "optional_title"
}
```

### Analyze Batch

```
POST /api/v1/analyze-batch
Body:
{
  "frames": [
    {
      "frame": "base64_encoded_image",
      "timestamp": 123.45,
      "video_id": "optional_id",
      "video_title": "optional_title"
    }
  ]
}
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```
NIM_API_KEY=your_nvidia_nim_api_key_here
NIM_API_ENDPOINT=https://integrate.api.nvidia.com/v1/chat/completions
NIM_MODEL_NAME=nvidia/nemotron-nano-12b-v2-vl
HOST=0.0.0.0
PORT=8000
DEBUG=True
MAX_FRAME_SIZE=1024
CONFIDENCE_THRESHOLD=0.7
```

## Features

- ✅ Real-time frame extraction from YouTube videos
- ✅ AI artifact detection using NVIDIA Nemotron model
- ✅ Detailed inconsistency reporting
- ✅ Configurable backend API URL
- ✅ Health check and connection status
- ✅ Batch frame analysis
- ✅ Modern, responsive UI
- ✅ Error handling and graceful degradation

## Technical Notes

### Frame Extraction

Frames are extracted every 5 seconds by default using the HTML5 Canvas API from the YouTube video element.

### AI Analysis

The backend uses NVIDIA's NIM API with the Nemotron-nano-12b-v2-vl vision-language model to detect:

- Facial artifacts
- Lighting inconsistencies
- Edge artifacts
- Temporal discontinuities
- Background anomalies
- Synthetic textures

### CORS Configuration

The backend is configured to accept requests from Chrome extensions and localhost for development.

## Troubleshooting

1. **Backend not connecting**: Check that the server is running and the URL in extension settings is correct
2. **API key errors**: Verify your NIM API key in the `.env` file
3. **Frame extraction fails**: Ensure the YouTube video is playing (not paused)
4. **Analysis times out**: Check your network connection and NIM API status

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
