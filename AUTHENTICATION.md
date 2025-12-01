# دليل التحقق من API Key - Authentication Guide

## نظرة عامة

السيرفر يدعم التحقق من API Key باستخدام Bearer Token في header `Authorization`. هذا ضروري لضمان الاتصال الآمن مع Vapi.

## الإعداد

### 1. إنشاء ملف `.env`

قم بنسخ `config.env.example` إلى `.env`:

```bash
copy config.env.example .env  # Windows
# أو
cp config.env.example .env    # Linux/Mac
```

### 2. تعيين API Key

افتح ملف `.env` وأضف API Key قوي:

```env
API_KEY=your-very-secret-api-key-here-change-this
```

**نصائح لإنشاء API Key قوي:**
- استخدم مفتاح طويل (32+ حرف)
- استخدم مزيج من أحرف كبيرة وصغيرة وأرقام ورموز
- لا تستخدم كلمات شائعة أو معلومات شخصية
- مثال: `sk-proj-abc123xyz789def456ghi012jkl345mno678pqr901stu234vwx567`

### 3. إعادة تشغيل السيرفر

بعد تعديل `.env`، أعد تشغيل السيرفر لتحميل القيم الجديدة.

## الاستخدام

### في الطلبات (Requests)

#### cURL
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key-here" \
  -d '{
    "model": "custom-llm-v1",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

#### Python
```python
import requests

API_KEY = "your-api-key-here"

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "custom-llm-v1",
        "messages": [{"role": "user", "content": "Hello"}]
    },
    headers={
        "Authorization": f"Bearer {API_KEY}"
    }
)
```

#### JavaScript
```javascript
const API_KEY = 'your-api-key-here';

fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`
  },
  body: JSON.stringify({
    model: 'custom-llm-v1',
    messages: [{ role: 'user', content: 'Hello' }]
  })
});
```

## التكامل مع Vapi

في إعدادات Vapi Custom LLM:

1. **URL:** `https://your-server.com/v1/chat/completions`
2. **Authorization Header:** `Bearer your-api-key-from-env-file`

## Endpoints المحمية

الـ endpoints التالية تتطلب API Key:
- ✅ `/v1/chat/completions` - Chat Completions endpoint
- ✅ `/vapi/custom-llm` - Vapi custom endpoint

الـ endpoints التالية **غير محمية** (للفحص فقط):
- `/health` - Health check
- `/v1/models` - List models

## معالجة الأخطاء

### 401 Unauthorized - Missing Authorization Header
```json
{
  "error": {
    "message": "Missing Authorization header. Please provide API key in Authorization: Bearer <key> format.",
    "type": "authentication_error",
    "code": "missing_authorization"
  }
}
```

### 401 Unauthorized - Invalid API Key
```json
{
  "error": {
    "message": "Invalid API key",
    "type": "authentication_error",
    "code": "invalid_api_key"
  }
}
```

## وضع التطوير (Development Mode)

إذا لم يتم تعيين `API_KEY` في ملف `.env`، سيتم **تعطيل التحقق تلقائياً** لتسهيل التطوير.

⚠️ **تحذير:** لا تستخدم هذا في بيئة الإنتاج! تأكد دائماً من تعيين API Key قوي.

## الأمان

### أفضل الممارسات:

1. ✅ **لا تشارك API Key علناً** - لا تضعه في الكود أو في Git
2. ✅ **استخدم HTTPS** في بيئة الإنتاج
3. ✅ **استخدم API Key قوي** - مفتاح طويل ومعقد
4. ✅ **غيّر API Key بانتظام** - خاصة إذا تم تسريبه
5. ✅ **استخدم متغيرات البيئة** - لا تكتب API Key مباشرة في الكود
6. ✅ **أضف `.env` إلى `.gitignore`** - لمنع رفعه إلى Git

### ما يجب تجنبه:

❌ لا تكتب API Key مباشرة في الكود  
❌ لا ترفع ملف `.env` إلى Git  
❌ لا تشارك API Key عبر قنوات غير آمنة  
❌ لا تستخدم API Keys ضعيفة أو قصيرة  

## استكشاف الأخطاء

### المشكلة: "Missing Authorization header"

**الحل:** تأكد من إضافة header `Authorization: Bearer <API_KEY>` في الطلب.

### المشكلة: "Invalid API Key"

**الحل:** 
1. تحقق من أن API Key في `.env` مطابق تماماً للـ key المرسل
2. تأكد من عدم وجود مسافات إضافية
3. تأكد من استخدام صيغة `Bearer <API_KEY>` وليس فقط `<API_KEY>`

### المشكلة: السيرفر لا يطلب API Key

**الحل:** تحقق من أن `API_KEY` معرّف في ملف `.env`. إذا لم يكن معرّفاً، سيتم تعطيل التحقق (للتطوير فقط).

## أمثلة إضافية

### استخدام متغيرات البيئة في Python
```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

# استخدام API_KEY في الطلبات
```

### اختبار API Key
```python
import requests

API_KEY = "your-api-key"

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={"messages": [{"role": "user", "content": "test"}]},
    headers={"Authorization": f"Bearer {API_KEY}"}
)

if response.status_code == 200:
    print("✅ API Key صحيح!")
elif response.status_code == 401:
    print("❌ API Key غير صحيح أو مفقود")
```

