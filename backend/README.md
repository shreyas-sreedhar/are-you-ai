# AI Video Fakeness Detector - Backend API

FastAPI backend server for analyzing video frames using NVIDIA's Nemotron-nano-12b-v2-vl model via NIM API.

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env and add your NVIDIA NIM API key
```

3. **Run the server:**

```bash
uvicorn main:app --reload --port 8000
```

Or use Python directly:

```bash
python main.py
```

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
      "video_id": "optional_id",
      "timestamp": 123.45,
      "video_title": "optional_title"
    }
  ]
}
```

## Environment Variables

See `.env.example` for all available configuration options.

## Testing

Test the API with curl or Postman:

```bash
curl -X GET http://localhost:8000/api/v1/health
```

# AI Video + News Detector Backend

## .env example

```
NIM_API_KEY=your_key
NIM_API_ENDPOINT=https://integrate.api.nvidia.com/v1/chat/completions
NIM_MODEL_NAME=nvidia/nemotron-nano-12b-v2-vl
HOST=0.0.0.0
PORT=8000
DEBUG=True
MAX_FRAME_SIZE=1024
CONFIDENCE_THRESHOLD=0.7
# Frame sequence
FRAME_SEQUENCE_LENGTH=5
FRAME_INTERVAL_MS=200
MIN_INCONSISTENCIES=2
# News/Text models
MODEL_REASON=meta/llama-3.1-405b-instruct
MODEL_FACT=nvidia/llama-3.1-nemotron-70b-instruct
MODEL_EXTRACT=meta/llama-3.1-70b-instruct
# Client base URL
BACKEND_BASE_URL=http://localhost:8000
```

## Internal client

- `services/backend_client.py` provides async helpers to call this API from Python.
