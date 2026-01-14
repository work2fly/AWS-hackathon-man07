"""
HTTP Audio Processing Handler
🏆 Breaking Barriers UK 2026 compliant
Processes audio via REST API instead of WebSocket
"""

import json
import boto3
import base64
from datetime import datetime

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

def invoke_bedrock_nova_sonic(audio_data_base64):
    """
    Invoke Amazon Nova Sonic 2 for speech-to-speech AI therapy
    🏆 Uses permitted Bedrock model (Amazon Nova Sonic 2)
    """
    try:
        print("🎤 Invoking Nova Sonic 2 for voice-to-voice...")
        
        # Nova Sonic 2 model ID
        model_id = "us.amazon.nova-sonic-v1:0"
        
        # System prompt for therapeutic conversation
        system_prompt = """You are Ally, a compassionate AI therapist providing mental health support.

Your role:
- Listen actively and empathetically
- Provide evidence-based therapeutic guidance
- Maintain professional boundaries
- Recognize emotional distress
- Encourage healthy coping mechanisms
- Never provide medical diagnoses

Communication style:
- Use warm, supportive language
- Ask open-ended questions
- Validate emotions
- Maintain cultural sensitivity

Keep responses concise and conversational (2-3 sentences max)."""
        
        # Prepare request body for Nova Sonic 2
        request_body = {
            "schemaVersion": "messages-v1",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": {
                                "format": "wav",
                                "source": {
                                    "bytes": audio_data_base64
                                }
                            }
                        }
                    ]
                }
            ],
            "system": [
                {
                    "text": system_prompt
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        print(f"📤 Sending audio to Nova Sonic 2 (model: {model_id})...")
        
        # Invoke Bedrock with rate limiting (stay below 1 RPS)
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        print(f"✅ Nova Sonic 2 response received: {response_body.keys()}")
        
        # Extract audio from response
        if 'content' in response_body:
            for content_block in response_body['content']:
                if 'audio' in content_block:
                    audio_response = content_block['audio']
                    print("✅ Audio response extracted from Nova Sonic 2")
                    return {
                        'audio': audio_response.get('source', {}).get('bytes', ''),
                        'format': audio_response.get('format', 'wav'),
                        'text': response_body.get('text', '')
                    }
        
        print("⚠️ No audio in Nova Sonic 2 response")
        return None
        
    except Exception as e:
        print(f"❌ Bedrock Nova Sonic error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def lambda_handler(event, context):
    """
    HTTP POST /process-audio handler
    Processes audio and returns AI response
    """
    try:
        # Enable CORS
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Content-Type': 'application/json'
        }
        
        # Handle OPTIONS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        session_id = body.get('sessionId')
        audio_data = body.get('audioData')
        audio_format = body.get('format', 'webm')
        sample_rate = body.get('sampleRate', 16000)
        
        print(f"📨 Processing audio for session: {session_id}")
        print(f"Audio format: {audio_format}, Sample rate: {sample_rate}")
        print(f"Audio data length: {len(audio_data) if audio_data else 0} bytes (base64)")
        
        if not audio_data:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'No audio data provided'})
            }
        
        # Process with Nova Sonic 2
        ai_response = invoke_bedrock_nova_sonic(audio_data)
        
        if ai_response and ai_response.get('audio'):
            print("✅ Returning AI response")
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'audioData': ai_response.get('audio'),
                    'format': ai_response.get('format', 'wav'),
                    'text': ai_response.get('text', ''),
                    'sessionId': session_id,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        else:
            print("❌ No AI response")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'AI processing failed'})
            }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
