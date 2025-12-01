"""
سكريبت لاختبار endpoint /v1/chat/completions
Script to test the /v1/chat/completions endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# URL السيرفر
BASE_URL = "http://localhost:8000"

# API Key from environment
API_KEY = os.getenv('API_KEY', None)

def test_chat_completions():
    """اختبار endpoint chat completions"""
    
    # بيانات الطلب
    payload = {
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
        "stream": False
    }
    
    print("=" * 50)
    print("اختبار Chat Completions Endpoint")
    print("=" * 50)
    print(f"\nإرسال الطلب إلى: {BASE_URL}/v1/chat/completions")
    print(f"\nالبيانات المرسلة:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("\n" + "-" * 50)
    
    # Prepare headers with API Key if available
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
        print(f"Using API Key: {API_KEY[:10]}...")
    else:
        print("⚠️  Warning: API_KEY not set in .env file. Request may fail if server requires authentication.")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print("\nالرد المستلم:")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("\n" + "-" * 50)
            print("✅ النجاح! تم استلام الرد بنجاح.")
            print(f"الرد من الـ LLM: {result['choices'][0]['message']['content']}")
        else:
            print(f"❌ خطأ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ خطأ: لا يمكن الاتصال بالسيرفر. تأكد من أن السيرفر يعمل على", BASE_URL)
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")


def test_streaming():
    """اختبار streaming response"""
    
    payload = {
        "model": "custom-llm-v1",
        "messages": [
            {"role": "user", "content": "أخبرني قصة قصيرة"}
        ],
        "temperature": 0.8,
        "stream": True
    }
    
    print("\n" + "=" * 50)
    print("اختبار Streaming Response")
    print("=" * 50)
    print(f"\nإرسال الطلب إلى: {BASE_URL}/v1/chat/completions (stream=True)")
    
    # Prepare headers with API Key if available
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            headers=headers,
            stream=True
        )
        
        print(f"Status Code: {response.status_code}")
        print("\nالرد المستلم (streaming):")
        print("-" * 50)
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_str = line_text[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            print("\n[Streaming completed]")
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                        except json.JSONDecodeError:
                            pass
            print("\n" + "-" * 50)
            print("✅ النجاح! تم استلام الرد المتدفق بنجاح.")
        else:
            print(f"❌ خطأ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ خطأ: لا يمكن الاتصال بالسيرفر.")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")


def test_health():
    """اختبار health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("\n" + "=" * 50)
        print("اختبار Health Check")
        print("=" * 50)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")


if __name__ == "__main__":
    print("بدء اختبارات السيرفر...")
    print("\n")
    
    # اختبار health check أولاً
    test_health()
    
    # اختبار chat completions
    test_chat_completions()
    
    # اختبار streaming
    test_streaming()
    
    print("\n" + "=" * 50)
    print("انتهت جميع الاختبارات")
    print("=" * 50)

