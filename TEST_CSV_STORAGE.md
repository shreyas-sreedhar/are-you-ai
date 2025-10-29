# ✅ Testing CSV Storage

## Quick Test Commands

### 1️⃣ Start Backend (New Terminal)
```bash
cd /Users/shreyas/Documents/Hackathon/are-you-ai/backend
python3 main.py
```

**Look for this line:**
```
INFO: CSV Storage initialized at: .../backend/data
```

---

### 2️⃣ Test Health Endpoint
```bash
curl http://localhost:8000/api/v1/health
```

**Expected:**
```json
{"status":"healthy","nim_api_configured":true}
```

---

### 3️⃣ Test Dashboard Metrics
```bash
curl http://localhost:8000/api/v1/dashboard/metrics
```

**Expected (initially):**
```json
{
  "videos_protected": 0,
  "scams_detected": 0,
  "messages_analyzed": 0,
  "active_alerts": 0
}
```

---

### 4️⃣ Analyze a Video (from Extension)
1. Open YouTube
2. Watch any video
3. Click "Analyze" in extension
4. Watch backend logs

**Expected log:**
```
INFO: Saved video analysis: <video_id>
```

---

### 5️⃣ Check CSV File
```bash
cd backend/data
cat videos.csv
```

**Expected:**
```csv
timestamp,video_id,platform,video_title,is_likely_fake,confidence_score,reasoning,analysis_result
2025-10-29T18:50:00.123456,abc123,youtube,Test Video,False,0.35,"...","{...}"
```

---

### 6️⃣ Check Dashboard
```bash
curl http://localhost:8000/api/v1/dashboard/metrics
```

**Expected (after analysis):**
```json
{
  "videos_protected": 1,
  "scams_detected": 0,
  "messages_analyzed": 0,
  "active_alerts": 0
}
```

---

### 7️⃣ Check Alerts
```bash
curl http://localhost:8000/api/v1/dashboard/alerts
```

**Expected:**
```json
[
  {
    "id": "video_abc123_2025-...",
    "timestamp": "2025-10-29T18:50:00.123456",
    "type": "video",
    "source": "youtube",
    "title": "Test Video",
    "risk_level": "MEDIUM",
    "description": "...",
    "confidence": 0.35
  }
]
```

---

### 8️⃣ Open Next.js Dashboard
```bash
cd /Users/shreyas/Documents/Hackathon/are-you-ai/web
npm run dev
```

Open: http://localhost:3000/dashboard

**Expected:**
- Real metrics (not hardcoded!)
- Recent alerts showing
- Live data from CSV files

---

## File Structure

After analyzing some videos and messages:

```
backend/
├── data/                    # ← NEW! CSV storage folder
│   ├── videos.csv          # Video analysis results
│   └── messages.csv        # Message scam detections
├── services/
│   ├── csv_storage.py      # ← NEW! CSV storage service
│   ├── frame_analyzer.py
│   └── ...
└── ...
```

---

## What Changed Summary

### ✅ **Added:**
- `backend/services/csv_storage.py` - CSV storage service
- `backend/data/` - Data folder (auto-created)
- `backend/.gitignore` - Ignores CSV files

### ❌ **Removed:**
- `backend/config/supabase.py` - Supabase config
- `supabase` from requirements.txt
- `supabase_url` and `supabase_key` from settings

### 🔄 **Modified:**
- `backend/api/routes.py` - Uses CSV storage
- `backend/api/dashboard_routes.py` - Reads from CSV
- `backend/config/settings.py` - Removed Supabase fields

---

## Benefits

✅ **Zero setup** - No external services  
✅ **Fast** - Local file access  
✅ **Simple** - Just CSV files  
✅ **Portable** - Easy to backup/share  
✅ **Transparent** - Open in Excel  
✅ **Hackathon-ready** - Works immediately  

---

🎉 **Try it now!** Start the backend and analyze a video!

