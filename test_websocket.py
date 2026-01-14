#!/usr/bin/env python3
"""
Quick WebSocket test script
🏆 Breaking Barriers UK 2026 compliant
"""

import asyncio
import websockets
import json
import base64
import ssl
from datetime import datetime

WEBSOCKET_URL = "wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev"

async def test_websocket():
    """Test WebSocket connection and message flow"""
    try:
        print(f"🔗 Connecting to {WEBSOCKET_URL}...")
        
        # Create SSL context that doesn't verify certificates (for testing only)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(WEBSOCKET_URL, ssl=ssl_context) as websocket:
            print("✅ Connected!")
            
            # Wait for welcome message
            try:
                welcome = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Received: {welcome}")
            except asyncio.TimeoutError:
                print("⏱️ No welcome message received (timeout)")
            
            # Send control message to start session
            control_message = {
                "type": "control",
                "payload": {
                    "action": "start_session",
                    "sessionId": f"test_session_{datetime.now().timestamp()}"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"📤 Sending control message: {control_message}")
            await websocket.send(json.dumps(control_message))
            
            # Wait for acknowledgment
            try:
                ack = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Received ACK: {ack}")
            except asyncio.TimeoutError:
                print("⏱️ No ACK received (timeout)")
            
            # Send a test audio message (empty base64 for testing)
            audio_message = {
                "type": "audio",
                "payload": {
                    "audioData": base64.b64encode(b"test audio data").decode('utf-8'),
                    "format": "wav",
                    "sampleRate": 44100
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"📤 Sending audio message...")
            await websocket.send(json.dumps(audio_message))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📨 Received response: {response[:200]}...")
            except asyncio.TimeoutError:
                print("⏱️ No response received (timeout)")
            
            print("✅ Test completed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 WebSocket Test Script")
    print("=" * 50)
    asyncio.run(test_websocket())
