# 🗄️ Supabase Database Setup

## Quick Setup (5 Minutes)

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign in with GitHub
3. Click "New Project"
4. Fill in:
   - **Project name**: `trustguard-ai`
   - **Database Password**: (create a strong password)
   - **Region**: Choose closest to you
5. Click "Create new project" (takes ~2 minutes)

### 2. Get Your Credentials

Once project is ready:

1. Go to **Settings** (gear icon on left)
2. Click **API** in the sidebar
3. Copy these two values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (under "Project API keys")

### 3. Add to `.env` File

Open `/Users/shreyas/Documents/Hackathon/are-you-ai/backend/.env` and add:

```env
# Existing configuration
NIM_API_KEY=your_nvidia_key_here
NIM_API_ENDPOINT=https://integrate.api.nvidia.com/v1/chat/completions
NIM_MODEL_NAME=nvidia/nemotron-nano-12b-v2-vl

# NEW - Add these lines
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key_here
```

### 4. Create Database Tables

1. In Supabase dashboard, click **SQL Editor** (left sidebar)
2. Click **New Query**
3. Copy and paste this SQL:

```sql
-- Videos table
CREATE TABLE videos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    video_title TEXT,
    analysis_result JSONB NOT NULL,
    is_likely_fake BOOLEAN NOT NULL,
    confidence_score DECIMAL NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_session TEXT
);

CREATE INDEX idx_videos_platform ON videos(platform);
CREATE INDEX idx_videos_timestamp ON videos(timestamp DESC);
CREATE INDEX idx_videos_is_fake ON videos(is_likely_fake);

-- Messages table
CREATE TABLE messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    message_text TEXT NOT NULL,
    sender TEXT,
    platform TEXT NOT NULL,
    analysis_result JSONB NOT NULL,
    scam_risk_score DECIMAL NOT NULL,
    risk_level TEXT NOT NULL,
    detected_scam_types TEXT[],
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_session TEXT
);

CREATE INDEX idx_messages_platform ON messages(platform);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_risk ON messages(risk_level);
```

4. Click **Run** (or press Cmd+Enter)
5. You should see "Success. No rows returned"

### 5. Restart Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Supabase client initialized successfully
```

---

## ✅ Verify It's Working

### Test 1: Analyze a Video

1. Go to YouTube
2. Click "Start" on any video
3. Check backend logs for: `Saved video analysis to Supabase`

### Test 2: Check Dashboard

1. Visit `http://localhost:3000/dashboard`
2. Metrics should show real numbers (not 0)
3. Alerts should appear if any content was flagged

### Test 3: View Data in Supabase

1. Go to Supabase dashboard
2. Click **Table Editor**
3. Select `videos` or `messages` table
4. You should see your analysis data!

---

## 🐛 Troubleshooting

### "SUPABASE_URL and SUPABASE_KEY must be set"

**Solution**: Check your `.env` file has the correct values with no extra spaces:
```bash
# In backend directory
cat .env | grep SUPABASE
```

### "Extra inputs are not permitted"

**Solution**: Already fixed! Just restart:
```bash
cd backend
python main.py
```

### Dashboard shows 0 for everything

**Possible causes:**
1. No videos analyzed yet → Analyze a video first
2. Supabase not connected → Check backend logs
3. CORS issue → Backend logs will show errors

### Can't connect to Supabase

1. **Check credentials**:
   ```bash
   # Test with Python
   python -c "from config.supabase import SupabaseClient; print('✅ Connected' if SupabaseClient.get_client() else '❌ Failed')"
   ```

2. **Check Supabase project is running**:
   - Go to Supabase dashboard
   - Make sure project shows "Active" status

3. **Check network**:
   - Supabase requires internet connection
   - Check firewall isn't blocking

---

## 📊 Dashboard Features Now Working

With Supabase connected:

✅ **Real-time metrics** - Actual counts from database
✅ **Alert history** - Shows flagged videos/messages
✅ **Persistent data** - Survives server restarts
✅ **Analytics** - Track trends over time
✅ **Multi-device** - Dashboard works from any device

---

## 🔒 Security Notes

### Free Tier Limits:
- ✅ 500 MB database storage
- ✅ 2 GB bandwidth/month
- ✅ 50,000 monthly active users
- ✅ Perfect for hackathon demo!

### Production Tips:
1. Use Row Level Security (RLS) policies
2. Create separate API keys for production
3. Enable database backups
4. Monitor usage in Supabase dashboard

---

## 🎉 You're Done!

Your TrustGuard AI system now has:
- ✅ Persistent database storage
- ✅ Real-time dashboard with actual data
- ✅ Full analysis history
- ✅ Professional data management

**Test it:**
1. Analyze some videos on YouTube
2. Open dashboard: `http://localhost:3000/dashboard`
3. See real metrics and alerts!

**For judges:**
- Show Supabase dashboard with actual data
- Demonstrate data persistence across restarts
- Prove it's production-ready with real database

🚀 Ready to demo!

