# 🚀 Quick Setup Guide

Follow these steps to get your Fatwa RAG system running.

---

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] Supabase account with fatwas database
- [ ] Qdrant Cloud account (free tier is fine)
- [ ] At least 4GB RAM available
- [ ] Stable internet connection

---

## 📋 Step-by-Step Setup

### Step 1: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows (Command Prompt):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Mac/Linux:
source venv/bin/activate

# Install all packages
pip install -r requirements.txt
```

**Expected time:** 3-5 minutes

---

### Step 2: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# Use any text editor (notepad, VSCode, etc.)
```

**Required values in .env:**

```env
# Supabase (get from supabase.com dashboard)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...  # Your anon/public key

# Qdrant (get from cloud.qdrant.io dashboard)
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=xxxxx

# Collection name (default is fine)
QDRANT_COLLECTION_NAME=fatwas
```

**Where to find credentials:**

**Supabase:**
1. Go to [supabase.com](https://supabase.com)
2. Open your project
3. Settings → API
4. Copy `URL` and `anon public` key

**Qdrant:**
1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a cluster (free tier)
3. Copy cluster URL and API key

---

### Step 3: Test Connections

```bash
# Quick test to verify everything is configured
python -c "
from app.config import settings
print('✓ Config loaded')
print(f'Supabase: {settings.supabase_url}')
print(f'Qdrant: {settings.qdrant_url}')
"
```

**Expected output:**
```
✓ Config loaded
Supabase: https://xxxxx.supabase.co
Qdrant: https://xxxxx.qdrant.io
```

---

### Step 4: Index Fatwas into Qdrant

This is a **one-time operation** that creates embeddings for all 22,397 fatwas.

```bash
python scripts/index_fatwas.py
```

**What happens:**
1. Fetches all fatwas from Supabase
2. Downloads embedding models (~100MB each)
3. Generates embeddings for all fatwas
4. Uploads to Qdrant

**Expected time:** 15-25 minutes (first time only)

**Progress output:**
```
[INFO] Fetching fatwas from Supabase...
[INFO] ✓ Fetched 22397 fatwas
[INFO] Loading embedding model: intfloat/multilingual-e5-small
[INFO] Generating embeddings (this may take a while)...
[INFO] Embedding batch 1/10
[INFO] Embedding batch 2/10
...
[INFO] ✓ Indexing completed successfully!
```

**If you need to reindex later:**
```bash
python scripts/index_fatwas.py --recreate
```

---

### Step 5: Start the API Server

```bash
python app/main.py
```

**Expected output:**
```
[INFO] Starting Fatwa RAG System
[INFO] Embedding Model: intfloat/multilingual-e5-small
[INFO] Reranker Model: cross-encoder/ms-marco-MiniLM-L-6-v2
[INFO] Services ready. Models will be loaded on first request.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Server is now running at:**
- API: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/health`

---

### Step 6: Test the System

**Option A: Using the test script**

Open a **new terminal** (keep server running) and run:

```bash
# Activate venv first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Test with a query
python scripts/test_search.py --query "وش حكم الصلاة بالشورت؟"
```

**Option B: Using the API docs**

1. Open browser: `http://localhost:8000/docs`
2. Find `POST /api/search`
3. Click "Try it out"
4. Enter query:
   ```json
   {
     "query": "ما حكم الصيام بدون سحور؟",
     "limit": 5
   }
   ```
5. Click "Execute"

**Option C: Using curl**

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"ما حكم الزكاة؟","limit":3}'
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Health check returns status "ok"
  ```bash
  curl http://localhost:8000/api/health
  ```

- [ ] Search returns results
  ```bash
  curl -X POST http://localhost:8000/api/search \
    -H "Content-Type: application/json" \
    -d '{"query":"حكم الصلاة"}'
  ```

- [ ] Test script works
  ```bash
  python scripts/test_search.py --query "ما حكم الصيام؟"
  ```

---

## 🐛 Common Issues

### Issue: `ModuleNotFoundError: No module named 'app'`
**Solution:** Make sure you're in the project root directory and venv is activated.

### Issue: Models downloading slowly
**Solution:** Models download on first use (~200MB total). Be patient. They're cached after first download.

### Issue: `Connection refused` to Qdrant/Supabase
**Solution:**
1. Check `.env` file has correct URLs and keys
2. Verify network connection
3. Check if services are running (Qdrant cluster, Supabase project)

### Issue: Indexing fails midway
**Solution:**
```bash
# Clear collection and restart
python scripts/index_fatwas.py --recreate
```

### Issue: Low search quality
**Solution:**
1. Check confidence thresholds in `.env`
2. Verify indexing completed (22,397 fatwas)
3. Test with different queries

---

## 📝 Next Steps

After successful setup:

1. **Read the full [README.md](README.md)** for detailed documentation
2. **Explore API endpoints** at `http://localhost:8000/docs`
3. **Run test suite** with `python scripts/test_search.py --suite`
4. **Adjust configuration** in `.env` based on your needs
5. **Integrate with your application** using the REST API

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs in terminal for error messages
2. Verify all prerequisites are met
3. Review this guide step-by-step
4. Check [README.md](README.md) troubleshooting section

---

**Happy searching! 🕌**
