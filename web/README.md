# AI Detector Web (Next.js)

Developer UI for detecting fake videos and fake news using the Python backend (NVIDIA NIM).

## Run

1. Configure backend URL

```
# create .env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

2. Install dependencies

```
npm i
```

3. Start dev server

```
npm run dev
```

## Pages

- / — Tabs for Video and News

## Client service

Requests are made via `web/lib/api.ts` to:

- POST /api/v1/analyze-frame
- POST /api/v1/analyze-sequence (stubbed for future use)
- POST /api/v1/analyze-text
