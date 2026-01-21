#!/bin/bash
# Test API Gateway endpoint directly
echo "Testing API Gateway endpoint..."
echo ""

curl -v -X POST https://xi8ekw0fj6.execute-api.us-west-2.amazonaws.com/dev/process-audio \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test_session_123",
    "audioData": "dGVzdGF1ZGlvZGF0YQ==",
    "format": "webm",
    "sampleRate": 16000
  }' 2>&1
