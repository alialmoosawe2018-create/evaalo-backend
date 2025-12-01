"""
Flask Backend Server for Custom LLM Integration with Vapi
This server provides HTTP endpoints that Vapi can connect to as a Custom LLM source.
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from functools import wraps
import json
import logging
import os
from typing import Dict, List, Any
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Vapi connections

# Configuration
PORT = int(os.getenv('PORT', 8000))
HOST = os.getenv('HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
API_KEY = os.getenv('API_KEY', None)  # API Key for authentication

# Validate API Key is set
if not API_KEY:
    logger.warning("⚠️  API_KEY not set in .env file. API authentication will be disabled.")
    logger.warning("⚠️  For production use, please set API_KEY in .env file for security.")
else:
    logger.info("✅ API Key authentication enabled")


class CustomLLM:
    """
    Custom LLM handler class
    You can integrate your own LLM logic here (OpenAI, Anthropic, local models, etc.)
    """
    
    def __init__(self):
        self.default_model = os.getenv('MODEL_NAME', 'custom-llm')
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Any:
        """
        Generate a response based on the conversation messages.
        
        Args:
            messages: List of message objects with 'role' (user/system/assistant) and 'content'
            model: Model name to use for generation
            temperature: Temperature parameter for response generation (0.0 to 2.0)
            stream: Whether to stream the response
            
        Returns:
            Response text or generator for streaming
        """
        # Use provided model or default
        model_name = model or self.default_model
        
        # Validate and clamp temperature
        temperature = max(0.0, min(2.0, float(temperature)))
        
        # Validate messages format
        if not isinstance(messages, list) or len(messages) == 0:
            raise ValueError("Messages must be a non-empty list")
        
        # Validate each message has required fields
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                raise ValueError(f"Message {i} must be a dictionary")
            if 'role' not in msg or 'content' not in msg:
                raise ValueError(f"Message {i} must have 'role' and 'content' fields")
            if msg['role'] not in ['user', 'system', 'assistant']:
                raise ValueError(f"Message {i} has invalid role: {msg['role']}. Must be 'user', 'system', or 'assistant'")
        
        # Extract the last user message for demo purposes
        user_message = None
        system_message = None
        
        for msg in messages:
            if msg.get('role') == 'system':
                system_message = msg.get('content', '')
            elif msg.get('role') == 'user':
                user_message = msg.get('content', '')
        
        # TODO: Replace this with your actual LLM inference logic
        # Example response - Replace this with your actual LLM integration
        response_text = f"هذه استجابة تجريبية من Custom LLM (Model: {model_name}, Temperature: {temperature}). الرسالة المستلمة: {user_message}"
        
        if stream:
            # Return a generator for streaming responses
            return self._stream_response(response_text, model_name)
        else:
            return response_text
    
    def _stream_response(self, text: str, model_name: str):
        """Generate streaming response tokens in OpenAI format"""
        words = text.split()
        for word in words:
            chunk_data = {
                'id': f"chatcmpl-{int(time.time())}",
                'object': 'chat.completion.chunk',
                'created': int(time.time()),
                'model': model_name,
                'choices': [{
                    'index': 0,
                    'delta': {'content': word + ' '},
                    'finish_reason': None
                }]
            }
            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
            time.sleep(0.05)  # Simulate streaming delay
        
        # Final chunk
        final_chunk = {
            'id': f"chatcmpl-{int(time.time())}",
            'object': 'chat.completion.chunk',
            'created': int(time.time()),
            'model': model_name,
            'choices': [{
                'index': 0,
                'delta': {},
                'finish_reason': 'stop'
            }]
        }
        yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


# Initialize LLM handler
llm = CustomLLM()


def require_api_key(f):
    """
    Decorator to require API Key authentication via Authorization header
    Format: Authorization: Bearer <API_KEY>
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If API_KEY is not set, skip authentication (for development)
        if not API_KEY:
            return f(*args, **kwargs)
        
        # Get Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            logger.warning("API request rejected: Missing Authorization header")
            return jsonify({
                'error': {
                    'message': 'Missing Authorization header. Please provide API key in Authorization: Bearer <key> format.',
                    'type': 'authentication_error',
                    'code': 'missing_authorization'
                }
            }), 401
        
        # Check if header starts with "Bearer "
        if not auth_header.startswith('Bearer '):
            logger.warning("API request rejected: Invalid Authorization header format")
            return jsonify({
                'error': {
                    'message': 'Invalid Authorization header format. Expected: Bearer <key>',
                    'type': 'authentication_error',
                    'code': 'invalid_authorization_format'
                }
            }), 401
        
        # Extract the API key
        provided_key = auth_header[7:]  # Remove "Bearer " prefix
        
        # Validate API key
        if provided_key != API_KEY:
            logger.warning(f"API request rejected: Invalid API key (attempted: {provided_key[:10]}...)")
            return jsonify({
                'error': {
                    'message': 'Invalid API key',
                    'type': 'authentication_error',
                    'code': 'invalid_api_key'
                }
            }), 401
        
        # API key is valid, proceed with the request
        logger.debug("API request authenticated successfully")
        return f(*args, **kwargs)
    
    return decorated_function


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok"}), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'custom-llm-server',
        'version': '1.0.0'
    }), 200


@app.route('/v1/chat/completions', methods=['POST'])
@require_api_key
def chat_completions():
    """
    Main endpoint for chat completions (OpenAI-compatible format)
    This is the standard endpoint that Vapi expects for Custom LLM integration
    
    Expected JSON format:
    {
        "model": "model-name",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ],
        "temperature": 0.7,
        "stream": false
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'message': 'No JSON data provided',
                    'type': 'invalid_request_error',
                    'code': 'missing_json'
                }
            }), 400
        
        # Extract and validate required fields
        messages = data.get('messages', [])
        if not messages:
            return jsonify({
                'error': {
                    'message': 'No messages provided. Messages must be a non-empty array.',
                    'type': 'invalid_request_error',
                    'code': 'missing_messages'
                }
            }), 400
        
        # Extract optional fields with defaults
        model = data.get('model', None)  # Will use default if not provided
        temperature = data.get('temperature', 0.7)  # Default temperature
        stream = data.get('stream', False)
        
        # Validate temperature range
        try:
            temperature = float(temperature)
            if not (0.0 <= temperature <= 2.0):
                return jsonify({
                    'error': {
                        'message': f'Temperature must be between 0.0 and 2.0, got {temperature}',
                        'type': 'invalid_request_error',
                        'code': 'invalid_temperature'
                    }
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'error': {
                    'message': f'Invalid temperature value: {temperature}',
                    'type': 'invalid_request_error',
                    'code': 'invalid_temperature'
                }
            }), 400
        
        # Determine model name for response
        model_name = model or llm.default_model
        
        logger.info(f"Received chat request - Model: {model_name}, Messages: {len(messages)}, Temperature: {temperature}, Stream: {stream}")
        
        # Generate response using LLM
        try:
            response_text = llm.generate_response(
                messages=messages,
                model=model,
                temperature=temperature,
                stream=stream
            )
        except ValueError as ve:
            return jsonify({
                'error': {
                    'message': str(ve),
                    'type': 'invalid_request_error',
                    'code': 'invalid_messages'
                }
            }), 400
        
        if stream:
            # Return streaming response in Server-Sent Events format
            return Response(
                response_text,
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
        else:
            # Return non-streaming response in Chat Completions format
            # Calculate token usage (simplified - replace with actual tokenizer if needed)
            prompt_tokens = sum(len(str(msg).split()) for msg in messages)
            completion_tokens = len(response_text.split())
            
            return jsonify({
                'id': f"chatcmpl-{int(time.time() * 1000)}",
                'object': 'chat.completion',
                'created': int(time.time()),
                'model': model_name,
                'choices': [{
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': response_text
                    },
                    'finish_reason': 'stop'
                }],
                'usage': {
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error in chat_completions: {str(e)}", exc_info=True)
        return jsonify({
            'error': {
                'message': f'Internal server error: {str(e)}',
                'type': 'server_error',
                'code': 'internal_error'
            }
        }), 500


@app.route('/vapi/custom-llm', methods=['POST'])
@require_api_key
def vapi_custom_llm():
    """
    Vapi-specific custom LLM endpoint
    Supports the same parameters as /v1/chat/completions but returns Vapi-compatible format
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        logger.info(f"Received Vapi request: {json.dumps(data, ensure_ascii=False)}")
        
        # Extract conversation data (supports both formats)
        messages = data.get('messages', [])
        if not messages:
            messages = data.get('conversation', [])
        
        if not messages:
            return jsonify({'error': 'No messages or conversation found'}), 400
        
        # Extract optional parameters
        model = data.get('model', None)
        temperature = data.get('temperature', 0.7)
        
        # Validate temperature
        try:
            temperature = float(temperature)
            temperature = max(0.0, min(2.0, temperature))
        except (ValueError, TypeError):
            temperature = 0.7
        
        # Generate response
        try:
            response_text = llm.generate_response(
                messages=messages,
                model=model,
                temperature=temperature,
                stream=False
            )
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        
        model_name = model or llm.default_model
        
        return jsonify({
            'response': response_text,
            'model': model_name,
            'temperature': temperature,
            'timestamp': int(time.time())
        }), 200
        
    except Exception as e:
        logger.error(f"Error in vapi_custom_llm: {str(e)}", exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/v1/models', methods=['GET'])
def list_models():
    """List available models (OpenAI-compatible)"""
    return jsonify({
        'object': 'list',
        'data': [{
            'id': llm.model_name,
            'object': 'model',
            'created': int(time.time()),
            'owned_by': 'custom-llm'
        }]
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f"Starting Custom LLM Server on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    app.run(host=HOST, port=PORT, debug=DEBUG)

