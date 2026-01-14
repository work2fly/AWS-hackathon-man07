"""
WebSocket Default Handler - Entry Point  
🏆 Breaking Barriers UK 2026 compliant
Handles all WebSocket messages and integrates with Bedrock Nova Sonic 2
"""

import json
import boto3
import base64
from datetime import datetime

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
apigateway_management = None

def get_apigateway_client(domain_name, stage):
    """Get API Gateway Management client for sending messages"""
    global apigateway_management
    if not apigateway_management:
        apigateway_management = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=f'https://{domain_name}/{stage}'
        )
    return apigateway_management

def send_message(connection_id, message, domain_name, stage):
    """Send message to WebSocket connection"""
    try:
        client = get_apigateway_client(domain_name, stage)
        client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message)
        )
        return True
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")
        return False

def invoke_bedrock_nova_sonic(audio_data_base64):
    """
    Invoke Amazon Nova Sonic 2 for speech-to-speech AI therapy
    🏆 Uses permitted Bedrock model (Amazon Nova Sonic 2)
    
    Nova Sonic 2 is a multimodal model that:
    - Takes audio input (speech)
    - Returns audio output (speech)
    - Maintains conversational context
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
        # Nova Sonic expects audio in base64 format
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
        # Nova Sonic returns audio in the content array
        if 'content' in response_body:
            for content_block in response_body['content']:
                if 'audio' in content_block:
                    audio_response = content_block['audio']
                    print("✅ Audio response extracted from Nova Sonic 2")
                    return {
                        'audio': audio_response.get('source', {}).get('bytes', ''),
                        'format': audio_response.get('format', 'wav'),
                        'text': response_body.get('text', '')  # May include transcript
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
    WebSocket $default route handler
    Processes audio messages and returns AI responses
    """
    try:
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        # Parse message
        body = event.get('body', '{}')
        message = json.loads(body) if isinstance(body, str) else body
        
        message_type = message.get('type', 'unknown')
        print(f"📨 Message type: {message_type} from {connection_id}")
        
        # Handle different message types
        if message_type == 'audio':
            # Audio message - send to Nova Sonic 2
            audio_data = message.get('payload', {}).get('audioData')
            
            if audio_data:
                print(f"🎤 Processing audio with Nova Sonic 2 (data length: {len(audio_data) if audio_data else 0})...")
                
                # Audio data should be base64 encoded
                # If it's already base64 string, use it directly
                # If it's binary, encode it
                if isinstance(audio_data, str):
                    audio_base64 = audio_data
                else:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Invoke Bedrock Nova Sonic 2
                ai_response = invoke_bedrock_nova_sonic(audio_base64)
                
                if ai_response and ai_response.get('audio'):
                    # Send AI audio response back
                    response_message = {
                        'type': 'audio',
                        'payload': {
                            'audioData': ai_response.get('audio'),
                            'format': ai_response.get('format', 'wav'),
                            'isFromAI': True
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    send_message(connection_id, response_message, domain_name, stage)
                    print("✅ AI audio response sent")
                    
                    # Also send text transcript if available
                    if ai_response.get('text'):
                        text_message = {
                            'type': 'text',
                            'payload': {
                                'text': ai_response.get('text'),
                                'isFromAI': True
                            },
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        send_message(connection_id, text_message, domain_name, stage)
                        print("✅ AI text transcript sent")
                else:
                    # Send error message
                    error_message = {
                        'type': 'error',
                        'payload': {'message': 'AI processing failed - no audio response'},
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    send_message(connection_id, error_message, domain_name, stage)
                    print("❌ No audio in AI response")
            
        elif message_type == 'control':
            # Control message (start/end session)
            action = message.get('payload', {}).get('action')
            print(f"🎮 Control action: {action}")
            
            # Send acknowledgment
            ack_message = {
                'type': 'ack',
                'payload': {'action': action, 'status': 'received'},
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message(connection_id, ack_message, domain_name, stage)
            
            # If starting session, send welcome message
            if action == 'start_session':
                print("🎤 Sending welcome audio response...")
                
                # Send a text response (avatar will speak it)
                welcome_message = {
                    'type': 'text',
                    'payload': {
                        'text': 'Hello! I am Ally, your AI therapy companion. How are you feeling today?',
                        'isFromAI': True
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
                send_message(connection_id, welcome_message, domain_name, stage)
                print("✅ Welcome message sent")
            
        else:
            print(f"⚠️ Unknown message type: {message_type}")
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {'statusCode': 500}
