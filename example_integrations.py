"""
أمثلة على كيفية دمج LLM حقيقي في CustomLLM class
Examples of how to integrate real LLM services into CustomLLM class
"""

import os
import json
from typing import List, Dict, Any


# ============================================
# مثال 1: التكامل مع OpenAI
# Example 1: OpenAI Integration
# ============================================
def openai_integration(messages: List[Dict[str, str]], stream: bool = False):
    """
    دمج OpenAI API
    """
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4'),
            messages=messages,
            stream=stream,
            temperature=0.7
        )
        
        if stream:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        else:
            return response.choices[0].message.content
            
    except ImportError:
        raise ImportError("Please install openai: pip install openai")
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


# ============================================
# مثال 2: التكامل مع Anthropic Claude
# Example 2: Anthropic Claude Integration
# ============================================
def anthropic_integration(messages: List[Dict[str, str]], stream: bool = False):
    """
    دمج Anthropic Claude API
    """
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Convert messages format for Anthropic
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                conversation_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        response = client.messages.create(
            model=os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229'),
            max_tokens=1024,
            system=system_message,
            messages=conversation_messages,
            stream=stream
        )
        
        if stream:
            for chunk in response:
                if chunk.type == 'content_block_delta':
                    if chunk.delta.text:
                        yield f"data: {json.dumps({'content': chunk.delta.text}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        else:
            return response.content[0].text
            
    except ImportError:
        raise ImportError("Please install anthropic: pip install anthropic")
    except Exception as e:
        raise Exception(f"Anthropic API error: {str(e)}")


# ============================================
# مثال 3: التكامل مع Local LLM (Ollama)
# Example 3: Local LLM Integration (Ollama)
# ============================================
def ollama_integration(messages: List[Dict[str, str]], stream: bool = False):
    """
    دمج Ollama (Local LLM)
    """
    try:
        import requests
        
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        model_name = os.getenv('OLLAMA_MODEL', 'llama2')
        
        response = requests.post(
            f"{ollama_url}/api/chat",
            json={
                'model': model_name,
                'messages': messages,
                'stream': stream
            },
            stream=stream,
            timeout=60
        )
        
        if stream:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        yield f"data: {json.dumps({'content': data['message']['content']}, ensure_ascii=False)}\n\n"
                    if data.get('done', False):
                        yield "data: [DONE]\n\n"
        else:
            data = response.json()
            return data.get('message', {}).get('content', '')
            
    except ImportError:
        raise ImportError("Please install requests: pip install requests")
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}")


# ============================================
# كيفية الاستخدام في app.py:
# How to use in app.py:
# ============================================
"""
في ملف app.py، قم بتعديل دالة generate_response في CustomLLM class:

class CustomLLM:
    def generate_response(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
        # اختر أحد الخيارات:
        # Choose one option:
        
        # Option 1: OpenAI
        return openai_integration(messages, stream)
        
        # Option 2: Anthropic
        return anthropic_integration(messages, stream)
        
        # Option 3: Ollama
        return ollama_integration(messages, stream)
        
        # Option 4: Multiple providers with fallback
        try:
            return openai_integration(messages, stream)
        except:
            return ollama_integration(messages, stream)
"""

