# 📦 دليل رفع ونشر المشروع

## ⚠️ قبل ما ترفع الكود

### أشياء **ما ترفعها أبداً:**

❌ ملف `.env` (فيه معلومات سرية!)
❌ مجلد `venv/` (بيئة Python)
❌ مجلد `frontend/node_modules/` (مكتبات Frontend)
❌ ملفات الـ cache والـ logs

✅ **تم إعداد `.gitignore` يمنع رفعها تلقائياً**

---

## 🚀 الطريقة 1: Repo واحد (موصى به)

### الخطوة 1: إنشاء Git Repository

```bash
cd c:\Users\hadee\Desktop\testff

# إنشاء git
git init

# إضافة جميع الملفات
git add .

# أول commit
git commit -m "Initial commit: Fatwa RAG System with Backend and Frontend"
```

### الخطوة 2: رفع على GitHub

**في موقع GitHub:**
1. اذهب إلى https://github.com/new
2. سمّي الـ repo مثلاً: `fatwa-rag-system`
3. **لا تضيف** README أو .gitignore (عندنا جاهزين)
4. اضغط Create

**في Terminal:**
```bash
# اربط مع GitHub (غير اسم المستخدم والـ repo)
git remote add origin https://github.com/YOUR_USERNAME/fatwa-rag-system.git

# ارفع الكود
git branch -M main
git push -u origin main
```

✅ **تم! الكود كله على GitHub**

---

## 🌐 الطريقة 2: نشر Frontend على Vercel

### الخطوة 1: ادخل Vercel

1. اذهب إلى: https://vercel.com
2. سجل دخول بحساب GitHub

### الخطوة 2: Import Project

1. اضغط **"New Project"**
2. اختر الـ repo: `fatwa-rag-system`
3. Vercel راح يكتشف Next.js تلقائياً

### الخطوة 3: إعدادات المشروع

**Root Directory:**
```
frontend
```

**Build Command:**
```
npm run build
```

**Output Directory:**
```
.next
```

**Environment Variables (مهم!):**
```
# لو تحتاج متغيرات، أضفها هنا
# مثلاً Backend URL
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### الخطوة 4: Deploy

اضغط **"Deploy"**

⏱️ **الانتظار 2-3 دقائق...**

✅ **تم! Frontend على الإنترنت** 🎉

رابطك: `https://your-app.vercel.app`

---

## 🖥️ نشر Backend على Railway

### الخطوة 1: ادخل Railway

1. اذهب إلى: https://railway.app
2. سجل دخول بحساب GitHub

### الخطوة 2: New Project

1. اضغط **"New Project"**
2. اختر **"Deploy from GitHub repo"**
3. اختر: `fatwa-rag-system`

### الخطوة 3: إعدادات

**Root Directory:**
```
.
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
```

### الخطوة 4: Deploy

✅ **Backend على الإنترنت!**

رابطك: `https://your-app.railway.app`

---

## 🔗 ربط Frontend بـ Backend

### بعد ما Backend ينشر:

1. **انسخ رابط Backend** من Railway
2. **عدّل Frontend:**

```bash
cd frontend
```

عدّل في `src/app/results/page.tsx`:

```typescript
const response = await axios.post(
  'https://YOUR-BACKEND-URL.railway.app/api/search',
  // ...
)
```

3. **ارفع التحديث:**

```bash
git add .
git commit -m "Update: Connect Frontend to deployed Backend"
git push
```

Vercel راح يعيد البناء تلقائياً!

---

## 📝 الملخص

### ما راح ترفعه:

- ✅ **الكود** (Backend + Frontend)
- ✅ **التوثيق** (README, guides)
- ✅ **إعدادات** (package.json, requirements.txt, configs)
- ✅ **الـ .gitignore**

### ما راح ترفعه أبداً:

- ❌ `.env` (معلومات سرية)
- ❌ `venv/` (بيئة Python)
- ❌ `node_modules/` (مكتبات Node)
- ❌ `.next/` (ملفات البناء)

---

## 🎯 الخطوات بالترتيب

1. ✅ **جهز الكود**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. ✅ **ارفع على GitHub**
   ```bash
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

3. ✅ **انشر Frontend** (Vercel)
   - Import من GitHub
   - Root: `frontend`
   - Deploy

4. ✅ **انشر Backend** (Railway)
   - Import من GitHub
   - أضف Environment Variables
   - Deploy

5. ✅ **اربطهم** (عدّل URL في Frontend)

---

## ⚡ نصائح

- **لا تنسى** `.env` في `.gitignore`
- **استخدم** Environment Variables في Vercel/Railway
- **اختبر** الـ deployment بعد كل تحديث
- **راقب** الـ logs لو في أخطاء

---

**جاهز للرفع! 🚀**
