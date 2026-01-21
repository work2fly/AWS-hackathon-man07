#!/usr/bin/env python3
"""
Test Lambda function directly without AWS CLI
"""

import sys
sys.path.insert(0, 'backend/src/lambda_functions')

from process_audio_http import lambda_handler
import json

# Test event
event = {
    'httpMethod': 'POST',
    'body': json.dumps({
        'sessionId': 'test123',
        'audioData': 'dGVzdGF1ZGlv',  # base64 "testaudio"
        'format': 'webm',
        'sampleRate': 16000
    })
}

context = {}

print("Testing Lambda function locally...")
print("=" * 60)

try:
    response = lambda_handler(event, context)
    print("Response:")
    print(json.dumps(response, indent=2))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
