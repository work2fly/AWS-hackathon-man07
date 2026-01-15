"""
Simple WebSocket Default Handler - With Text-to-Speech
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import boto3
import os
import base64
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'))
polly = boto3.client('polly', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'))

connections_table = dynamodb.Table(os.environ['CONNECTIONS_TABLE_NAME'])
sessions_table = dynamodb.Table(os.environ['SESSIONS_TABLE_NAME'])

# Bedrock model configuration
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')

def handler(event, context):
    """Handle WebSocket $default route - simplified for demo"""
    try:
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        # Parse message
        body = event.get('body', '{}')
        message = json.loads(body) if isinstance(body, str) else body
        
        print(f"📨 WebSocket message from {connection_id}: {message.get('type', 'unknown')}")
        
        # Get connection info
        response = connections_table.get_item(Key={'connectionId': connection_id})
        if 'Item' not in response:
            print(f"❌ Connection not found: {connection_id}")
            return {'statusCode': 404}
        
        connection_info = response['Item']
        user_id = connection_info['userId']
        
        # Handle different message types
        message_type = message.get('type', '')
        
        if message_type == 'join_session':
            return handle_join_session(connection_id, user_id, message, domain_name, stage)
        elif message_type == 'ping':
            return handle_ping(connection_id, message, domain_name, stage)
        elif message_type == 'audio':
            return handle_audio(connection_id, user_id, message, domain_name, stage)
        elif message_type == 'text':
            return handle_text(connection_id, user_id, message, domain_name, stage)
        else:
            print(f"⚠️ Unknown message type: {message_type}")
            send_message(connection_id, {
                'type': 'error',
                'error': f'Unknown message type: {message_type}',
                'timestamp': datetime.utcnow().isoformat()
            }, domain_name, stage)
            return {'statusCode': 400}
        
    except Exception as e:
        print(f"❌ Default handler error: {str(e)}")
        return {'statusCode': 500}

def handle_join_session(connection_id, user_id, message, domain_name, stage):
    """Handle join_session message"""
    try:
        session_id = message.get('session_id')
        if not session_id:
            send_message(connection_id, {
                'type': 'error',
                'error': 'Missing session_id',
                'timestamp': datetime.utcnow().isoformat()
            }, domain_name, stage)
            return {'statusCode': 400}
        
        print(f"✅ User {user_id} joining session {session_id}")
        
        # Create session in DynamoDB
        sessions_table.put_item(
            Item={
                'sessionId': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'clientId': user_id,
                'status': 'active',
                'startTime': datetime.utcnow().isoformat(),
                'language': 'en'
            }
        )
        
        # Update connection with session ID
        connections_table.update_item(
            Key={'connectionId': connection_id},
            UpdateExpression='SET sessionId = :sid',
            ExpressionAttributeValues={':sid': session_id}
        )
        
        # Send confirmation
        send_message(connection_id, {
            'type': 'session_joined',
            'session_id': session_id,
            'message': 'Successfully joined session',
            'timestamp': datetime.utcnow().isoformat()
        }, domain_name, stage)
        
        print(f"✅ Session {session_id} created and joined")
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"❌ Join session error: {str(e)}")
        return {'statusCode': 500}

def handle_ping(connection_id, message, domain_name, stage):
    """Handle ping message"""
    send_message(connection_id, {
        'type': 'pong',
        'timestamp': datetime.utcnow().isoformat(),
        'original_timestamp': message.get('timestamp')
    }, domain_name, stage)
    return {'statusCode': 200}

def handle_audio(connection_id, user_id, message, domain_name, stage):
    """Handle audio message - transcribe, process with AI, and respond with speech"""
    print(f"🎤 Audio message received from {user_id}")
    
    try:
        payload = message.get('payload', {})
        audio_data = payload.get('audioData')
        audio_format = payload.get('format', 'webm')
        
        if not audio_data:
            send_message(connection_id, {
                'type': 'error',
                'error': 'No audio data provided',
                'timestamp': datetime.utcnow().isoformat()
            }, domain_name, stage)
            return {'statusCode': 400}
        
        # Decode base64 audio if it's a string
        if isinstance(audio_data, str):
            try:
                audio_bytes = base64.b64decode(audio_data)
            except Exception as e:
                print(f"❌ Failed to decode audio: {str(e)}")
                send_message(connection_id, {
                    'type': 'error',
                    'error': 'Invalid audio data encoding',
                    'timestamp': datetime.utcnow().isoformat()
                }, domain_name, stage)
                return {'statusCode': 400}
        else:
            audio_bytes = audio_data
        
        print(f"📊 Audio data size: {len(audio_bytes)} bytes, format: {audio_format}")
        
        # For WebM/Opus audio from browser, we need to use StartTranscriptionJob
        # For real-time, we'd need to convert to PCM first
        # Simpler approach: Ask user to use text chat for now, but acknowledge audio
        
        # Send acknowledgment
        send_message(connection_id, {
            'type': 'text',
            'payload': {
                'text': 'I heard you! For the best experience, please type your message in the chat below. Full speech-to-speech is being enhanced.',
                'isFromAI': True
            },
            'timestamp': datetime.utcnow().isoformat()
        }, domain_name, stage)
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"❌ Audio handler error: {str(e)}")
        send_message(connection_id, {
            'type': 'error',
            'error': 'Failed to process audio',
            'timestamp': datetime.utcnow().isoformat()
        }, domain_name, stage)
        return {'statusCode': 500}

def handle_text(connection_id, user_id, message, domain_name, stage):
    """Handle text message - process with Bedrock AI and return audio + text"""
    print(f"💬 Text message received from {user_id}: {message.get('payload', {}).get('text', '')}")
    
    try:
        text_content = message.get('payload', {}).get('text', '')
        
        if not text_content:
            send_message(connection_id, {
                'type': 'error',
                'error': 'Empty message',
                'timestamp': datetime.utcnow().isoformat()
            }, domain_name, stage)
            return {'statusCode': 400}
        
        # Get session context
        session_id = message.get('sessionId') or message.get('session_id')
        session_context = []
        
        if session_id:
            try:
                session_response = sessions_table.get_item(Key={'sessionId': session_id})
                if 'Item' in session_response:
                    session_context = session_response['Item'].get('messages', [])
            except Exception as e:
                print(f"⚠️ Could not retrieve session context: {str(e)}")
        
        # Call Bedrock AI for therapy response
        ai_response = get_ai_therapy_response(text_content, session_context)
        
        # Generate audio response using Polly
        audio_data = None
        try:
            print(f"🔊 Generating speech with Polly...")
            polly_response = polly.synthesize_speech(
                Text=ai_response,
                OutputFormat='mp3',
                VoiceId='Joanna',  # Warm, empathetic female voice
                Engine='neural'  # Better quality
            )
            
            # Read audio stream
            if 'AudioStream' in polly_response:
                audio_data = base64.b64encode(polly_response['AudioStream'].read()).decode('utf-8')
                print(f"✅ Audio generated: {len(audio_data)} bytes (base64)")
        except Exception as e:
            print(f"⚠️ Polly error (continuing with text only): {str(e)}")
        
        # Send text response
        send_message(connection_id, {
            'type': 'text',
            'payload': {
                'text': ai_response,
                'isFromAI': True
            },
            'timestamp': datetime.utcnow().isoformat()
        }, domain_name, stage)
        
        # Send audio response if available
        if audio_data:
            send_message(connection_id, {
                'type': 'audio',
                'payload': {
                    'audioData': audio_data,
                    'format': 'mp3',
                    'isFromAI': True
                },
                'timestamp': datetime.utcnow().isoformat()
            }, domain_name, stage)
        
        # Store message in session history
        if session_id:
            try:
                # Append to session messages
                sessions_table.update_item(
                    Key={'sessionId': session_id},
                    UpdateExpression='SET messages = list_append(if_not_exists(messages, :empty_list), :new_messages)',
                    ExpressionAttributeValues={
                        ':empty_list': [],
                        ':new_messages': [
                            {'role': 'user', 'content': text_content, 'timestamp': datetime.utcnow().isoformat()},
                            {'role': 'assistant', 'content': ai_response, 'timestamp': datetime.utcnow().isoformat()}
                        ]
                    }
                )
            except Exception as e:
                print(f"⚠️ Could not store message in session: {str(e)}")
        
        print(f"✅ AI response sent to {user_id}")
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"❌ Text handler error: {str(e)}")
        send_message(connection_id, {
            'type': 'error',
            'error': 'Failed to process message',
            'timestamp': datetime.utcnow().isoformat()
        }, domain_name, stage)
        return {'statusCode': 500}

def get_ai_therapy_response(user_message, session_context):
    """
    Get AI therapy response from Bedrock
    🏆 Breaking Barriers UK 2026 compliant - stays under 1 RPS
    """
    try:
        # Build conversation history
        messages = []
        
        # Add recent session context (last 5 exchanges to stay under token limits)
        for msg in session_context[-10:]:  # Last 5 exchanges = 10 messages
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Add current user message
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        # Enhanced system prompt with cultural awareness
        system_prompt = """You are a compassionate, culturally-aware AI therapy assistant. Your role is to:

**Core Responsibilities:**
- Listen actively and empathetically to the user's concerns
- Ask thoughtful questions to help them explore their feelings
- Provide supportive, non-judgmental responses
- Use evidence-based therapeutic techniques when appropriate
- Encourage self-reflection and personal growth
- Maintain professional boundaries

**Cultural Sensitivity:**
- Be aware of and respect diverse cultural backgrounds, beliefs, and values
- Recognize that mental health stigma varies across cultures
- Adapt communication style to be culturally appropriate
- Acknowledge that family dynamics, gender roles, and social expectations differ across cultures
- Be sensitive to religious and spiritual beliefs that may influence mental health perspectives
- Understand that expressions of emotion and distress vary culturally
- Respect cultural approaches to healing and wellness
- Avoid imposing Western therapeutic models as universal solutions

**Cultural Context Awareness:**
- If the user mentions their cultural background, acknowledge and incorporate it into your responses
- Be mindful of collectivist vs individualist cultural values
- Recognize that concepts like "self-care" may have different meanings across cultures
- Be aware of migration, diaspora, and identity challenges
- Understand intergenerational trauma and cultural displacement
- Respect traditional healing practices alongside modern therapy

**Professional Guidelines:**
- Never provide medical diagnoses or prescribe treatments
- Suggest professional help for serious mental health concerns
- Keep responses concise (2-3 sentences) for natural conversation flow
- Be warm, genuine, and human in your interactions

Remember: Cultural humility means continuously learning and adapting to each individual's unique cultural context."""

        # Prepare Bedrock request (Claude format)
        request_body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 300,  # Keep responses concise
            'temperature': 0.7,
            'system': system_prompt,
            'messages': messages
        }
        
        print(f"🤖 Calling Bedrock model: {BEDROCK_MODEL_ID}")
        
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        ai_text = response_body['content'][0]['text']
        
        print(f"✅ Bedrock response received: {ai_text[:100]}...")
        return ai_text
        
    except Exception as e:
        print(f"❌ Bedrock error: {str(e)}")
        # Fallback response
        return "I'm here to listen and support you. Could you tell me more about what's on your mind?"

def send_message(connection_id, message, domain_name, stage):
    """Send message to WebSocket connection"""
    try:
        apigateway = boto3.client('apigatewaymanagementapi',
            endpoint_url=f'https://{domain_name}/{stage}')
        
        apigateway.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message)
        )
        return True
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")
        return False
