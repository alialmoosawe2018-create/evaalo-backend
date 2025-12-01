# وثائق API - Custom LLM Server

## Endpoint: `/v1/chat/completions`

### الوصف
Endpoint رئيسي متوافق مع OpenAI API format لاستقبال طلبات Chat Completions وإرجاع الردود.

### Method
`POST`

### Headers
```
Content-Type: application/json
Authorization: Bearer <API_KEY>
```

**ملاحظة مهمة:** يجب إضافة API Key في header `Authorization` بصيغة `Bearer <API_KEY>`. يتم تعيين API Key في ملف `.env` كمتغير `API_KEY`.

### Request Body

#### الحقول المطلوبة:
- **`messages`** (array, required): قائمة الرسائل في المحادثة
  - كل رسالة يجب أن تحتوي على:
    - `role` (string, required): نوع الرسالة - يجب أن يكون واحد من: `"user"`, `"system"`, `"assistant"`
    - `content` (string, required): محتوى الرسالة

#### الحقول الاختيارية:
- **`model`** (string, optional): اسم النموذج المراد استخدامه. إذا لم يتم تحديده، سيتم استخدام النموذج الافتراضي.
- **`temperature`** (float, optional): قيمة temperature للتحكم في عشوائية الرد (0.0 إلى 2.0). القيمة الافتراضية: `0.7`
- **`stream`** (boolean, optional): إذا كان `true`، سيتم إرجاع الرد بشكل متدفق (streaming). القيمة الافتراضية: `false`

### مثال Request

```json
{
  "model": "custom-llm-v1",
  "messages": [
    {
      "role": "system",
      "content": "أنت مساعد ذكي ومفيد. تحدث بالعربية."
    },
    {
      "role": "user",
      "content": "مرحباً، كيف حالك؟"
    },
    {
      "role": "assistant",
      "content": "مرحباً! أنا بخير، شكراً لسؤالك."
    },
    {
      "role": "user",
      "content": "ما هو الطقس اليوم؟"
    }
  ],
  "temperature": 0.7,
  "stream": false
}
```

### Response (Non-Streaming)

#### Success Response (200 OK)

```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "custom-llm-v1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "الرد من الـ LLM هنا..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 30,
    "total_tokens": 80
  }
}
```

#### Error Responses

**400 Bad Request - Missing Messages:**
```json
{
  "error": {
    "message": "No messages provided. Messages must be a non-empty array.",
    "type": "invalid_request_error",
    "code": "missing_messages"
  }
}
```

**400 Bad Request - Invalid Temperature:**
```json
{
  "error": {
    "message": "Temperature must be between 0.0 and 2.0, got 3.0",
    "type": "invalid_request_error",
    "code": "invalid_temperature"
  }
}
```

**400 Bad Request - Invalid Messages Format:**
```json
{
  "error": {
    "message": "Message 0 must have 'role' and 'content' fields",
    "type": "invalid_request_error",
    "code": "invalid_messages"
  }
}
```

**401 Unauthorized - Missing Authorization Header:**
```json
{
  "error": {
    "message": "Missing Authorization header. Please provide API key in Authorization: Bearer <key> format.",
    "type": "authentication_error",
    "code": "missing_authorization"
  }
}
```

**401 Unauthorized - Invalid API Key:**
```json
{
  "error": {
    "message": "Invalid API key",
    "type": "authentication_error",
    "code": "invalid_api_key"
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": {
    "message": "Internal server error: ...",
    "type": "server_error",
    "code": "internal_error"
  }
}
```

### Response (Streaming)

عندما يكون `stream: true`، يتم إرجاع الرد بصيغة Server-Sent Events (SSE).

#### Content-Type
```
text/event-stream
```

#### Format
كل chunk يأتي بصيغة:
```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"custom-llm-v1","choices":[{"index":0,"delta":{"content":"كلمة "},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"custom-llm-v1","choices":[{"index":0,"delta":{"content":"أخرى "},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"custom-llm-v1","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### أمثلة الاستخدام

#### باستخدام cURL (Non-Streaming)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key-here" \
  -d '{
    "model": "custom-llm-v1",
    "messages": [
      {"role": "user", "content": "مرحباً"}
    ],
    "temperature": 0.7,
    "stream": false
  }'
```

#### باستخدام Python

```python
import requests

API_KEY = "your-api-key-here"

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "custom-llm-v1",
        "messages": [
            {"role": "user", "content": "مرحباً"}
        ],
        "temperature": 0.7,
        "stream": False
    },
    headers={
        "Authorization": f"Bearer {API_KEY}"
    }
)

result = response.json()
print(result["choices"][0]["message"]["content"])
```

#### باستخدام JavaScript (Fetch)

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
    messages: [
      { role: 'user', content: 'مرحباً' }
    ],
    temperature: 0.7,
    stream: false
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Endpoint: `/health`

### الوصف
للتحقق من حالة السيرفر.

### Method
`GET`

### Response (200 OK)

```json
{
  "status": "healthy",
  "service": "custom-llm-server",
  "version": "1.0.0"
}
```

## Endpoint: `/v1/models`

### الوصف
لعرض النماذج المتاحة.

### Method
`GET`

### Response (200 OK)

```json
{
  "object": "list",
  "data": [
    {
      "id": "custom-llm",
      "object": "model",
      "created": 1234567890,
      "owned_by": "custom-llm"
    }
  ]
}
```

## ملاحظات مهمة

1. **API Authentication**: يجب إضافة API Key في header `Authorization: Bearer <API_KEY>`. يتم تعيين API Key في ملف `.env` كمتغير `API_KEY`. إذا لم يتم تعيين API_KEY، سيتم تعطيل التحقق (للتطوير فقط).
2. **Validation**: يتم التحقق من صحة جميع المدخلات قبل المعالجة
3. **Temperature**: يجب أن تكون القيمة بين 0.0 و 2.0
4. **Messages Roles**: يجب أن تكون `role` واحدة من: `user`, `system`, `assistant`
5. **Streaming**: عند استخدام streaming، يجب معالجة الرد كـ Server-Sent Events
6. **Error Handling**: جميع الأخطاء تُرجع بصيغة JSON موحدة

## التكامل مع Vapi

للاستخدام مع Vapi، قم بإضافة URL السيرفر في إعدادات Custom LLM:
```
https://your-server.com/v1/chat/completions
```

**في إعدادات Vapi، أضف API Key في حقل Authorization:**
```
Bearer your-api-key-from-env-file
```

تأكد من:
- السيرفر يدعم HTTPS (للإنتاج)
- السيرفر يمكن الوصول إليه من الإنترنت
- CORS مفعّل (مفعّل افتراضياً في الكود)
- API Key معرّف في ملف `.env` ومحمي بشكل جيد

