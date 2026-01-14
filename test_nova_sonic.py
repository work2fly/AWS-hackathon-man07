#!/usr/bin/env python3
"""
Test Nova Sonic 2 with Converse API
🏆 Breaking Barriers UK 2026 compliant
"""

import boto3
import json
import base64

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')

def test_nova_sonic_converse():
    """Test Nova Sonic 2 with Converse API"""
    
    print("🎤 Testing Nova Sonic 2 with Converse API...")
    
    # Create a simple audio test (silence - just for testing API)
    # In real use, this would be actual audio data
    test_audio = b'\x00' * 1000  # 1000 bytes of silence
    audio_base64 = base64.b64encode(test_audio).decode('utf-8')
    
    try:
        # Try Converse API
        print("📤 Attempting Converse API...")
        response = bedrock.converse(
            modelId='amazon.nova-2-sonic-v1:0',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'text': 'Hello, how are you?'
                        }
                    ]
                }
            ],
            inferenceConfig={
                'maxTokens': 100,
                'temperature': 0.7
            }
        )
        print("✅ Converse API SUCCESS!")
        print(json.dumps(response, indent=2, default=str))
        return True
        
    except Exception as e:
        print(f"❌ Converse API failed: {e}")
        
    try:
        # Try InvokeModel API with proper format
        print("\n📤 Attempting InvokeModel API...")
        
        request_body = {
            "schemaVersion": "messages-v1",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Hello, how are you?"
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 100,
                "temperature": 0.7
            }
        }
        
        response = bedrock.invoke_model(
            modelId='amazon.nova-2-sonic-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(request_body)
        )
        
        result = json.loads(response['body'].read())
        print("✅ InvokeModel API SUCCESS!")
        print(json.dumps(result, indent=2))
        return True
        
    except Exception as e:
        print(f"❌ InvokeModel API failed: {e}")
    
    return False

def test_claude_sonnet():
    """Test Claude Sonnet 4.5 as fallback"""
    
    print("\n🤖 Testing Claude Sonnet 4.5...")
    
    try:
        response = bedrock.converse(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'text': 'Say hello in one sentence.'
                        }
                    ]
                }
            ],
            inferenceConfig={
                'maxTokens': 100,
                'temperature': 0.7
            }
        )
        
        print("✅ Claude Sonnet 4.5 SUCCESS!")
        
        # Extract response text
        if 'output' in response and 'message' in response['output']:
            content = response['output']['message']['content']
            for block in content:
                if 'text' in block:
                    print(f"💬 Response: {block['text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Claude Sonnet failed: {e}")
        return False

def test_polly():
    """Test Amazon Polly"""
    
    print("\n🔊 Testing Amazon Polly...")
    
    polly = boto3.client('polly', region_name='us-west-2')
    
    try:
        response = polly.synthesize_speech(
            Text='Hello, this is a test of Amazon Polly.',
            OutputFormat='mp3',
            VoiceId='Joanna',
            Engine='neural'
        )
        
        audio_data = response['AudioStream'].read()
        print(f"✅ Polly SUCCESS! Generated {len(audio_data)} bytes of audio")
        
        # Save to file for testing
        with open('/tmp/polly_test.mp3', 'wb') as f:
            f.write(audio_data)
        print("💾 Saved to /tmp/polly_test.mp3")
        
        return True
        
    except Exception as e:
        print(f"❌ Polly failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing AWS AI Services")
    print("=" * 60)
    
    # Test Nova Sonic 2
    sonic_works = test_nova_sonic_converse()
    
    # Test Claude Sonnet 4.5
    claude_works = test_claude_sonnet()
    
    # Test Polly
    polly_works = test_polly()
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Nova Sonic 2: {'✅ WORKING' if sonic_works else '❌ NOT WORKING'}")
    print(f"Claude Sonnet 4.5: {'✅ WORKING' if claude_works else '❌ NOT WORKING'}")
    print(f"Amazon Polly: {'✅ WORKING' if polly_works else '❌ NOT WORKING'}")
    print("=" * 60)
    
    if sonic_works:
        print("\n🎉 Nova Sonic 2 is working! Use it for voice-to-voice.")
    elif claude_works and polly_works:
        print("\n✅ Fallback: Use Claude + Polly pipeline")
    else:
        print("\n❌ No working solution found")
