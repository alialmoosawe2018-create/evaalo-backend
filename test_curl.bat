@echo off
REM سكريبت لاختبار endpoints باستخدام curl على Windows
REM Script to test endpoints using curl on Windows

set BASE_URL=http://localhost:8000
set API_KEY=%API_KEY%
if "%API_KEY%"=="" set API_KEY=your-api-key-here

echo ==========================================
echo اختبار Custom LLM Server Endpoints
echo Testing Custom LLM Server Endpoints
echo ==========================================
echo.

REM Test 1: Health Check
echo 1. اختبار Health Check Endpoint
echo    Testing Health Check Endpoint
echo ----------------------------------------
curl -X GET "%BASE_URL%/health" ^
  -H "Content-Type: application/json"
echo.
echo.

REM Test 2: Chat Completions (Non-Streaming)
echo 2. اختبار Chat Completions (Non-Streaming)
echo    Testing Chat Completions (Non-Streaming)
echo ----------------------------------------
curl -X POST "%BASE_URL%/v1/chat/completions" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %API_KEY%" ^
  -d "{\"model\": \"custom-llm-v1\", \"messages\": [{\"role\": \"system\", \"content\": \"أنت مساعد ذكي ومفيد. تحدث بالعربية.\"}, {\"role\": \"user\", \"content\": \"مرحباً، كيف حالك؟\"}], \"temperature\": 0.7, \"stream\": false}"
echo.
echo.

REM Test 3: List Models
echo 3. اختبار List Models Endpoint
echo    Testing List Models Endpoint
echo ----------------------------------------
curl -X GET "%BASE_URL%/v1/models" ^
  -H "Content-Type: application/json"
echo.
echo.

echo ==========================================
echo انتهت جميع الاختبارات
echo All tests completed
echo ==========================================
pause

