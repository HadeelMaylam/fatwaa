# 🚀 تشغيل النظام الكامل (Backend + Frontend)

## المتطلبات

- ✅ Python 3.9+
- ✅ Node.js 18+
- ✅ Supabase و Qdrant (معدّلة في `.env`)

---

## الخطوة 1: تشغيل Backend (FastAPI)

افتح **Terminal 1**:

```bash
# انتقل للمجلد الرئيسي
cd c:\Users\hadee\Desktop\testff

# فعّل البيئة الافتراضية
venv\Scripts\activate

# شغل FastAPI
python app/main.py
```

✅ **Backend يشتغل على:** `http://localhost:8000`

📄 **API Docs:** `http://localhost:8000/docs`

---

## الخطوة 2: تثبيت Frontend

افتح **Terminal 2** (جديد):

```bash
# انتقل لمجلد Frontend
cd c:\Users\hadee\Desktop\testff\frontend

# ثبت المكتبات (مرة واحدة فقط)
npm install
```

---

## الخطوة 3: تشغيل Frontend

في نفس **Terminal 2**:

```bash
# شغل Next.js
npm run dev
```

✅ **Frontend يشتغل على:** `http://localhost:3000`

---

## 🎉 افتح المتصفح

اذهب إلى: **http://localhost:3000**

---

## 📝 ملاحظات مهمة

### ⚠️ قبل ما تجرب البحث:

**لازم تفهرس الفتاوى أولاً!**

في **Terminal 3**:

```bash
cd c:\Users\hadee\Desktop\testff
venv\Scripts\activate
python scripts/index_fatwas.py --recreate
```

⏱️ **الفهرسة تاخذ 2-3 ساعات**

---

## 🔧 حل المشاكل

### مشكلة: Backend ما يشتغل

```bash
# تأكد أن venv مفعّل
venv\Scripts\activate

# أعد تثبيت المكتبات
pip install -r requirements.txt

# شغل Backend
python app/main.py
```

### مشكلة: Frontend ما يشتغل

```bash
# احذف node_modules وأعد التثبيت
rm -rf node_modules
npm install

# شغل Frontend
npm run dev
```

### مشكلة: "لم أجد فتوى"

- تأكد أن الفهرسة خلصت (`python scripts/index_fatwas.py`)
- تأكد أن Qdrant و Supabase شغالين
- شيك ملف `.env`

---

## 📊 الهيكل النهائي

```
testff/
├── app/                    # Backend (FastAPI)
│   ├── layers/            # 6 طبقات معالجة
│   ├── services/          # Supabase + Qdrant
│   └── api/               # Endpoints
│
├── frontend/              # Frontend (Next.js)
│   └── src/
│       └── app/
│           ├── page.tsx            # صفحة البحث
│           └── results/page.tsx   # صفحة النتائج
│
├── scripts/               # سكريبتات
│   ├── index_fatwas.py   # الفهرسة
│   └── test_search.py    # الاختبار
│
├── venv/                  # بيئة Python
└── .env                   # الإعدادات
```

---

## 🎯 Flow النظام

```
المستخدم يكتب سؤال في Frontend
         ↓
Frontend يرسل POST إلى Backend
         ↓
Backend يعالج السؤال (6 طبقات)
         ↓
Backend يبحث في Qdrant
         ↓
Backend يرجع النتائج
         ↓
Frontend يعرض البطاقات
```

---

## 🌐 النشر

### Backend

- Railway
- Render
- DigitalOcean

### Frontend

- Vercel (موصى به!)
- Netlify
- Cloudflare Pages

---

**كل شيء جاهز! 🚀**
