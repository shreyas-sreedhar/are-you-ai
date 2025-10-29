# 🚀 Simple Setup Guide - TrustGuard AI

## What Changed?
✅ **Removed Supabase** - No external database needed!  
✅ **Local CSV Storage** - Data saved to `backend/data/` folder  
✅ **Zero Configuration** - Just works out of the box  

---

## Quick Start (3 Steps)

### 1️⃣ Start Backend
```bash
cd /Users/shreyas/Documents/Hackathon/are-you-ai/backend
python3 main.py
```

✅ You should see:
```
INFO: CSV Storage initialized at: /Users/shreyas/.../backend/data
INFO: Application startup complete.
```

### 2️⃣ Start Dashboard
```bash
cd /Users/shreyas/Documents/Hackathon/are-you-ai/web
npm run dev
```

✅ Open: http://localhost:3000/dashboard

### 3️⃣ Load Extension
1. Open Chrome → Extensions → Load Unpacked
2. Select: `/Users/shreyas/Documents/Hackathon/are-you-ai/extension`
3. Done! 🎉

---

## How It Works

### **Data Storage** 📁
All data is stored locally in CSV files:
```
backend/data/
├── videos.csv      # Video analysis results
└── messages.csv    # Message scam detections
```

### **What Gets Saved** 💾

**Videos:**
- Video ID, platform, title
- AI detection results
- Confidence scores
- Timestamps

**Messages:**
- Sender, platform, message text
- Scam risk scores
- Detected scam types
- Warning details

---

## Test It! 🧪

### **Test Video Analysis:**
1. Go to YouTube or Facebook
2. Watch any video
3. Click the "Analyze" button in the extension
4. Check backend logs: `Saved video analysis: <video_id>`
5. Refresh dashboard → See new data!

### **Check CSV Files:**
```bash
cd backend/data
cat videos.csv
cat messages.csv
```

---

## Dashboard Features

✅ **Real-time metrics** - Videos protected, scams detected  
✅ **Recent alerts** - High-risk detections  
✅ **Protection status** - Active monitoring  
✅ **Multi-agent info** - 6 AI agents working together  

---

## Troubleshooting

### No data showing up?
1. Check if `backend/data/` folder exists
2. Look for CSV files: `videos.csv`, `messages.csv`
3. Check backend logs for "Saved video analysis" or "Saved message analysis"

### CSV files corrupted?
```bash
cd backend/data
rm videos.csv messages.csv
# Restart backend - files will be recreated
```

### Want to reset data?
```bash
cd backend/data
> videos.csv  # Clear but keep headers
> messages.csv
```

Or just delete the files:
```bash
rm videos.csv messages.csv
```

---

## Benefits of CSV Storage

✅ **Simple** - No external services to configure  
✅ **Fast** - Local file access  
✅ **Portable** - Easy to share/backup  
✅ **Transparent** - Open files in Excel/Google Sheets  
✅ **Hackathon-friendly** - Zero setup time  

---

## Demo Tips

1. **Show CSV files** - Open in Excel to show raw data
2. **Live updates** - Analyze a video, refresh dashboard immediately
3. **Export data** - CSV files can be opened anywhere
4. **No internet** - Works completely offline (after API calls)

---

🎉 **That's it!** No databases, no cloud services, just simple CSV files!

