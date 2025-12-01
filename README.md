# Custom LLM Server for Vapi

مشروع Backend مخصص لبناء سيرفر Python باستخدام Flask، يُستخدم كمصدر "Custom LLM" يمكن لـ Vapi الاتصال به عبر HTTP.

## المميزات

- ✅ سيرفر Flask جاهز للاستخدام
- ✅ دعم endpoints متوافقة مع OpenAI API
- ✅ دعم Streaming Responses
- ✅ **API Key Authentication** - حماية endpoints باستخدام Bearer Token
- ✅ CORS مفعّل للاتصال مع Vapi
- ✅ Health Check endpoint
- ✅ معالجة أخطاء شاملة
- ✅ Logging مفعّل

## المتطلبات

- Python 3.8 أو أحدث
- pip

## التثبيت

1. استنسخ المشروع أو قم بتحميل الملفات

2. قم بإنشاء بيئة افتراضية (Virtual Environment):
```bash
python -m venv venv
```

3. قم بتفعيل البيئة الافتراضية:
```bash
# على Windows
venv\Scripts\activate

# على Linux/Mac
source venv/bin/activate
```

4. قم بتثبيت التبعيات:
```bash
pip install -r requirements.txt
```

5. قم بنسخ ملف `config.env.example` إلى `.env` وتعديل الإعدادات:
```bash
copy config.env.example .env  # Windows
# أو
cp config.env.example .env    # Linux/Mac
```

6. **⚠️ مهم جداً:** قم بتعيين API Key في ملف `.env`:
```env
API_KEY=your-secret-api-key-here-change-this-in-production
```
هذا المفتاح ضروري لـ Vapi للاتصال بشكل آمن بالسيرفر.

## التشغيل

قم بتشغيل السيرفر:
```bash
python app.py
```

السيرفر سيعمل على `http://localhost:8000` بشكل افتراضي.

## Endpoints المتاحة

### 1. Health Check
```
GET /health
```
للتحقق من حالة السيرفر.

### 2. Chat Completions (OpenAI-compatible)
```
POST /v1/chat/completions
```
Endpoint رئيسي متوافق مع OpenAI API. يمكن لـ Vapi استخدامه مباشرة.

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "مرحباً"}
  ],
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "custom-llm",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "الرد من LLM"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 3. Vapi Custom LLM Endpoint
```
POST /vapi/custom-llm
```
Endpoint مخصص لـ Vapi (يمكن تخصيصه حسب متطلبات Vapi).

### 4. List Models
```
GET /v1/models
```
لعرض النماذج المتاحة.

## التكامل مع Vapi

1. قم بتشغيل السيرفر على خادم يمكن الوصول إليه من الإنترنت (أو استخدم ngrok للتطوير المحلي)

2. في إعدادات Vapi، أضف URL السيرفر:
   ```
   https://your-server.com/v1/chat/completions
   ```

3. **أضف API Key في إعدادات Vapi:**
   - في حقل Authorization، أضف: `Bearer <API_KEY>`
   - حيث `<API_KEY>` هو القيمة التي عرّفتها في ملف `.env`

4. تأكد من أن السيرفر يدعم HTTPS (مطلوب للإنتاج)

5. تأكد من أن API Key محمي ولا يتم مشاركته علناً

## التخصيص

### إضافة LLM حقيقي

قم بتعديل دالة `generate_response` في كلاس `CustomLLM` في ملف `app.py`:

```python
def generate_response(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
    # مثال مع OpenAI
    import openai
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=stream
    )
    
    if stream:
        for chunk in response:
            yield f"data: {json.dumps({'content': chunk.choices[0].delta.content or ''}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    else:
        return response.choices[0].message.content
```

### API Key Authentication

✅ **تم تفعيل API Key Authentication افتراضياً!**

التحقق من API Key يتم تلقائياً على جميع endpoints المهمة (`/v1/chat/completions` و `/vapi/custom-llm`).

**كيفية العمل:**
1. يتم قراءة API Key من ملف `.env` (متغير `API_KEY`)
2. يجب إرسال API Key في header: `Authorization: Bearer <API_KEY>`
3. إذا لم يتم تعيين `API_KEY` في `.env`، سيتم تعطيل التحقق (للتطوير فقط)

**ملاحظة:** في بيئة الإنتاج، تأكد دائماً من تعيين API Key قوي في ملف `.env`.

## النشر

### استخدام Gunicorn (للإنتاج)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### استخدام Docker

قم بإنشاء `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## الدعم

للمساعدة أو الاستفسارات، يرجى فتح issue في المشروع.

## الترخيص

MIT License

