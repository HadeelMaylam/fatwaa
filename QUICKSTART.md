# ⚡ Quick Start (5 Minutes)

Get the Fatwa RAG system running in 5 simple steps.

---

## 1️⃣ Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate     # Windows
# OR
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

---

## 2️⃣ Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials:
# - SUPABASE_URL (from supabase.com)
# - SUPABASE_KEY (from supabase.com)
# - QDRANT_URL (from cloud.qdrant.io)
# - QDRANT_API_KEY (from cloud.qdrant.io)
```

---

## 3️⃣ Index Fatwas (One-Time, ~20 min)

```bash
python scripts/index_fatwas.py
```

**Note:** This downloads models and creates embeddings for 22,397 fatwas. Only needed once.

---

## 4️⃣ Start Server

```bash
# Windows:
run.bat

# Mac/Linux:
chmod +x run.sh
./run.sh

# Or manually:
python app/main.py
```

Server runs at: `http://localhost:8000`

---

## 5️⃣ Test It

**In browser:**
- Go to `http://localhost:8000/docs`
- Try `POST /api/search` with:
  ```json
  {
    "query": "ما حكم الصلاة في البيت؟",
    "limit": 3
  }
  ```

**Or in terminal:**
```bash
python scripts/test_search.py --query "ما حكم الصيام؟"
```

---

## 🎉 Done!

You now have a working Fatwa RAG system.

**Next:**
- Read [README.md](README.md) for full documentation
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Explore API at `http://localhost:8000/docs`

---

## 🆘 Problems?

**Models downloading slowly?**
→ First time only. ~200MB total. Be patient.

**Connection errors?**
→ Check `.env` credentials are correct.

**No results?**
→ Make sure indexing completed successfully (Step 3).

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting.
