# LiveKit Integration Plan for AI Therapy Platform
🏆 Breaking Barriers UK 2026 Hackathon

## Executive Summary

This document outlines the integration of LiveKit with Amazon Nova Sonic 2 for the AI Therapy Platform hackathon. LiveKit provides production-ready WebRTC infrastructure that eliminates the need for custom audio streaming code, saving an estimated 20-25 hours of development time.

**Official AWS Support**: [Build real-time conversational AI experiences using Amazon Nova Sonic and LiveKit](https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/)

## Architecture Overview

```
┌─────────────────┐
│  React Client   │
│  LiveKit SDK    │
└────────┬────────┘
         │ WebRTC
         ↓
┌─────────────────┐
│ LiveKit Server  │
│   (ECS/EC2)     │
└────────┬────────┘
         │ Audio Stream
         ↓
┌─────────────────┐
│ LiveKit Agent   │
│ Nova Sonic      │
│ Plugin          │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ↓         ↓          ↓
┌────────┐ ┌──────┐ ┌─────────┐
│ Nova   │ │Lambda│ │AgentCore│
│ Sonic  │ │ APIs │ │ Memory  │
└────────┘ └──────┘ └─────────┘
```

## What LiveKit Provides

### 1. Client SDK (@livekit/components-react)
- ✅ Pre-built React components for audio rooms
- ✅ WebRTC connection management
- ✅ Microphone/speaker access
- ✅ Connection state handling
- ✅ Audio quality indicators
- ✅ TypeScript types

### 2. Server Infrastructure
- ✅ WebRTC SFU (Selective Forwarding Unit)
- ✅ Room and participant management
- ✅ Audio routing and optimization
- ✅ Load balancing
- ✅ Health monitoring

### 3. Agent Framework (Python)
- ✅ Voice AI agent orchestration
- ✅ Nova Sonic plugin (official AWS)
- ✅ Turn detection (knows when user stops speaking)
- ✅ Voice activity detection
- ✅ Noise suppression
- ✅ Multi-language support

## What We Still Build

### Core Therapeutic Features (Keep All)
- ✅ AgentCore memory integration (DONE - Task 2.1, 2.2, 2.3)
- ✅ Therapeutic prompts (DONE - Task 1.3)
- ✅ Session continuity service (DONE - Task 2.3)
- ✅ Red flag detection (TODO - Task 4.2, 4.3)
- ✅ Safety guardrails (TODO - Task 4.1)
- ✅ Sentiment analysis (TODO - Task 5.1)
- ✅ User authentication (Cognito)
- ✅ Session management (DynamoDB)
- ✅ Therapist notifications

### Integration Layer (New)
- 🆕 LiveKit token generation (Lambda)
- 🆕 LiveKit room creation (Lambda)
- 🆕 Agent context loading (Lambda → AgentCore)
- 🆕 Red flag event handling (Agent → Lambda)
- 🆕 Session persistence (Agent → DynamoDB)

## Implementation Phases

### Phase 1: Infrastructure Setup (2-3 hours)

#### 1.1 Deploy LiveKit Server on ECS
```bash
# Use official LiveKit Docker image
docker pull livekit/livekit-server:latest

# Deploy to ECS Fargate
# - Configure security groups (ports 7880, 50000-60000)
# - Set up Application Load Balancer
# - Configure Redis for state management
```

**ECS Task Definition**:
```json
{
  "family": "livekit-server",
  "containerDefinitions": [{
    "name": "livekit",
    "image": "livekit/livekit-server:latest",
    "portMappings": [
      {"containerPort": 7880, "protocol": "tcp"},
      {"containerPort": 7881, "protocol": "tcp"}
    ],
    "environment": [
      {"name": "LIVEKIT_CONFIG", "value": "/etc/livekit.yaml"}
    ],
    "secrets": [
      {"name": "LIVEKIT_KEYS", "valueFrom": "arn:aws:secretsmanager:..."}
    ]
  }]
}
```

#### 1.2 Configure LiveKit Server
```yaml
# livekit.yaml (store in Secrets Manager)
port: 7880
rtc:
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
  tcp_port: 7881
redis:
  address: ${REDIS_ENDPOINT}:6379
keys:
  ${API_KEY}: ${API_SECRET}
region: us-west-2
```

#### 1.3 Set Up LiveKit Agent Environment
```bash
# Create EC2 or ECS task for agent
# Install dependencies
pip install livekit-agents livekit-plugins-aws

# Configure AWS credentials for Bedrock access
export AWS_DEFAULT_REGION=us-west-2
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

### Phase 2: Backend Integration (3-4 hours)

#### 2.1 Create LiveKit Token Generator (Lambda)
```python
# lambda_functions/livekit_token_generator.py
import os
from livekit import api
import boto3

def handler(event, context):
    """Generate LiveKit access token for client"""
    
    # Get user info from Cognito
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    # Create session in DynamoDB
    session_id = create_therapy_session(user_id)
    room_name = f"session_{session_id}"
    
    # Generate LiveKit token
    token = api.AccessToken(
        api_key=os.environ['LIVEKIT_API_KEY'],
        api_secret=os.environ['LIVEKIT_API_SECRET']
    )
    token.with_identity(user_id)
    token.with_name(f"Client_{user_id[:8]}")
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True
    ))
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'token': token.to_jwt(),
            'room_name': room_name,
            'session_id': session_id,
            'server_url': os.environ['LIVEKIT_SERVER_URL']
        })
    }
```

#### 2.2 Create Context Loader API (Lambda)
```python
# lambda_functions/agent_context_loader.py
from services.session_continuity_service import SessionContinuityService
from services.therapeutic_prompt_service import TherapeuticPromptService

def handler(event, context):
    """Load therapeutic context for LiveKit agent"""
    
    room_name = event['room_name']
    session_id = room_name.replace('session_', '')
    client_id = get_client_id_from_session(session_id)
    
    # Load session continuity context (ALREADY IMPLEMENTED)
    continuity_service = SessionContinuityService()
    context = continuity_service.resume_conversation(
        client_id=client_id,
        new_session_id=session_id
    )
    
    # Get therapeutic prompts (ALREADY IMPLEMENTED)
    prompt_service = TherapeuticPromptService()
    system_prompt = prompt_service.get_system_prompt(
        language=context.get('language', 'en'),
        context=context['context']
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'system_prompt': system_prompt,
            'context': context,
            'client_id': client_id,
            'session_id': session_id
        })
    }
```

#### 2.3 Create Red Flag Handler (Lambda)
```python
# lambda_functions/red_flag_handler.py
from services.red_flag_detection_service import RedFlagDetectionService
from services.notification_service import NotificationService

def handler(event, context):
    """Handle red flag events from LiveKit agent"""
    
    session_id = event['session_id']
    transcript_segment = event['transcript']
    
    # Detect red flags (TO BE IMPLEMENTED in Task 4.2)
    detection_service = RedFlagDetectionService()
    red_flags = detection_service.detect_red_flags(transcript_segment)
    
    if red_flags:
        # Send notifications (ALREADY IMPLEMENTED)
        notification_service = NotificationService()
        for flag in red_flags:
            notification_service.send_red_flag_alert(
                session_id=session_id,
                flag_type=flag['type'],
                severity=flag['severity'],
                context=flag['context']
            )
    
    return {'statusCode': 200, 'red_flags_detected': len(red_flags)}
```

### Phase 3: LiveKit Agent Implementation (4-5 hours)

#### 3.1 Create Main Agent File
```python
# livekit_agent/agent.py
import asyncio
import logging
import os
import requests
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.plugins import aws

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoints
CONTEXT_API = os.environ['CONTEXT_LOADER_API']
RED_FLAG_API = os.environ['RED_FLAG_HANDLER_API']
SESSION_PERSIST_API = os.environ['SESSION_PERSIST_API']

async def load_therapeutic_context(room_name: str) -> dict:
    """Load context from Lambda API"""
    response = requests.post(CONTEXT_API, json={'room_name': room_name})
    return response.json()

async def check_red_flags(session_id: str, transcript: str):
    """Send transcript to red flag detection"""
    requests.post(RED_FLAG_API, json={
        'session_id': session_id,
        'transcript': transcript
    })

async def persist_session(room_name: str, conversation_data: list):
    """Persist session data to DynamoDB"""
    requests.post(SESSION_PERSIST_API, json={
        'room_name': room_name,
        'conversation_data': conversation_data
    })

async def entrypoint(ctx: JobContext):
    """Main agent entry point"""
    
    logger.info(f"Agent starting for room: {ctx.room.name}")
    
    # Load therapeutic context
    context_data = await load_therapeutic_context(ctx.room.name)
    system_prompt = context_data['system_prompt']
    session_id = context_data['session_id']
    
    logger.info(f"Loaded context for session: {session_id}")
    
    # Initialize Nova Sonic assistant
    assistant = aws.VoiceAssistant(
        model="amazon.nova-sonic-v1:0",
        system_prompt=system_prompt,
        temperature=0.7,
        # Therapeutic voice settings
        voice_settings={
            "stability": 0.8,
            "similarity_boost": 0.7
        }
    )
    
    # Track conversation for red flag detection
    conversation_turns = []
    
    # Monitor speech for red flags
    @assistant.on("user_speech_committed")
    async def on_user_speech(text: str):
        logger.info(f"User said: {text[:50]}...")
        conversation_turns.append({"user": text, "timestamp": asyncio.get_event_loop().time()})
        
        # Check for red flags
        await check_red_flags(session_id, text)
    
    @assistant.on("agent_speech_committed")
    async def on_agent_speech(text: str):
        logger.info(f"Agent said: {text[:50]}...")
        conversation_turns.append({"agent": text, "timestamp": asyncio.get_event_loop().time()})
    
    # Start the assistant
    assistant.start(ctx.room)
    
    # Wait for session to complete
    await ctx.wait_for_participant()
    
    # Persist session data
    logger.info(f"Session {session_id} completed, persisting data...")
    await persist_session(ctx.room.name, conversation_turns)
    
    logger.info(f"Agent finished for room: {ctx.room.name}")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

#### 3.2 Deploy Agent
```bash
# Run agent as ECS task or EC2 process
python agent.py start \
  --url wss://your-livekit-server.com \
  --api-key your-api-key \
  --api-secret your-api-secret
```

### Phase 4: Frontend Integration (3-4 hours)

#### 4.1 Install LiveKit SDK
```bash
npm install @livekit/components-react @livekit/rtc-client
```

#### 4.2 Create Therapy Session Component
```typescript
// src/components/client/TherapySession.tsx
import React, { useEffect, useState } from 'react';
import {
  LiveKitRoom,
  useVoiceAssistant,
  BarVisualizer,
  RoomAudioRenderer,
  VoiceAssistantControlBar
} from '@livekit/components-react';
import '@livekit/components-styles';

interface SessionData {
  token: string;
  room_name: string;
  session_id: string;
  server_url: string;
}

export function TherapySession() {
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get LiveKit token from backend
    fetch('/api/livekit/token', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
      }
    })
      .then(res => res.json())
      .then(data => {
        setSessionData(data);
        setLoading(false);
      });
  }, []);

  if (loading || !sessionData) {
    return <div>Preparing your therapy session...</div>;
  }

  return (
    <div className="therapy-session">
      <h2>Therapy Session</h2>
      <LiveKitRoom
        token={sessionData.token}
        serverUrl={sessionData.server_url}
        connect={true}
        audio={true}
        video={false}
        onDisconnected={() => {
          console.log('Session ended');
          // Navigate to session summary
        }}
      >
        <TherapySessionUI sessionId={sessionData.session_id} />
      </LiveKitRoom>
    </div>
  );
}

function TherapySessionUI({ sessionId }: { sessionId: string }) {
  const voiceAssistant = useVoiceAssistant();

  return (
    <div className="session-ui">
      {/* Audio renderer (handles playback) */}
      <RoomAudioRenderer />
      
      {/* Voice visualizer */}
      <div className="visualizer">
        <BarVisualizer
          state={voiceAssistant.state}
          barCount={5}
          trackRef={voiceAssistant.audioTrack}
        />
      </div>
      
      {/* Connection status */}
      <div className="status">
        Status: {voiceAssistant.state}
      </div>
      
      {/* Control bar */}
      <VoiceAssistantControlBar />
      
      {/* Session info */}
      <div className="session-info">
        Session ID: {sessionId}
      </div>
    </div>
  );
}
```

#### 4.3 Add to App Router
```typescript
// src/App.tsx
import { TherapySession } from './components/client/TherapySession';

function App() {
  return (
    <Routes>
      <Route path="/session" element={<TherapySession />} />
      {/* Other routes */}
    </Routes>
  );
}
```

### Phase 5: Testing & Validation (2-3 hours)

#### 5.1 Local Testing
```bash
# 1. Start LiveKit server locally
docker run --rm -p 7880:7880 -p 7881:7881 \
  -e LIVEKIT_KEYS="devkey: secret" \
  livekit/livekit-server

# 2. Start agent
python agent.py start --url ws://localhost:7880

# 3. Start frontend
npm run dev

# 4. Test session flow
```

#### 5.2 Integration Tests
- ✅ Token generation works
- ✅ Room creation successful
- ✅ Agent connects and loads context
- ✅ Audio flows client → agent → Nova Sonic
- ✅ Red flag detection triggers
- ✅ Session data persists

#### 5.3 End-to-End Test
1. Client logs in
2. Starts therapy session
3. Speaks to AI therapist
4. AI responds with therapeutic context
5. Red flag detected and notification sent
6. Session ends and data saved
7. Therapist sees session summary

## Deployment Checklist

### AWS Resources
- [ ] ECS cluster for LiveKit server
- [ ] ECS task definition with LiveKit image
- [ ] Application Load Balancer for LiveKit
- [ ] Security groups (7880, 7881, 50000-60000)
- [ ] ElastiCache Redis for LiveKit state
- [ ] Lambda functions (token gen, context loader, red flag handler)
- [ ] API Gateway REST API
- [ ] DynamoDB tables (add LiveKitRooms table)
- [ ] Secrets Manager (LiveKit API keys)
- [ ] CloudWatch logs and metrics

### Configuration
- [ ] LiveKit server config (livekit.yaml)
- [ ] Agent environment variables
- [ ] Lambda environment variables
- [ ] Frontend environment variables
- [ ] CORS configuration
- [ ] WAF rules

### Security
- [ ] TLS certificates for LiveKit server
- [ ] API Gateway authorizer (Cognito)
- [ ] IAM roles for Lambda
- [ ] Secrets rotation policy
- [ ] Network ACLs

## Cost Estimation (Hackathon)

**LiveKit Infrastructure**:
- ECS Fargate (2 vCPU, 4GB): ~$0.12/hour
- ElastiCache Redis (cache.t3.micro): ~$0.017/hour
- ALB: ~$0.025/hour
- **Total**: ~$0.16/hour = **$3.84/day**

**AWS Services** (existing):
- Lambda: Pay per invocation
- DynamoDB: Pay per request
- Bedrock (Nova Sonic): Pay per token
- **Estimated**: $5-10/day for testing

**Total Hackathon Cost**: ~$10-15/day

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1: Infrastructure | 2-3 hours | Deploy LiveKit server, configure ECS |
| Phase 2: Backend | 3-4 hours | Lambda functions, API endpoints |
| Phase 3: Agent | 4-5 hours | Python agent with Nova Sonic |
| Phase 4: Frontend | 3-4 hours | React components with LiveKit SDK |
| Phase 5: Testing | 2-3 hours | Integration and E2E tests |
| **Total** | **14-19 hours** | Full LiveKit integration |

**Time Saved vs Custom**: 20-25 hours (audio infrastructure eliminated)

## Success Criteria

✅ Client can join LiveKit room with token
✅ Audio streams to LiveKit agent
✅ Agent loads therapeutic context from AgentCore
✅ Nova Sonic responds with therapeutic prompts
✅ Red flags detected and notifications sent
✅ Session data persists to DynamoDB
✅ Therapist dashboard shows session summaries
✅ End-to-end latency < 500ms

## Troubleshooting

### Common Issues

**1. Agent can't connect to LiveKit server**
- Check security groups allow ports 7880, 7881
- Verify LiveKit API keys match
- Check agent has network access to server

**2. No audio in client**
- Check browser permissions for microphone
- Verify LiveKit token has correct grants
- Check WebRTC connection in browser console

**3. Nova Sonic errors**
- Verify AWS credentials in agent environment
- Check Bedrock quota limits
- Verify model ID: `amazon.nova-sonic-v1:0`

**4. Context not loading**
- Check Lambda API endpoints are accessible
- Verify AgentCore memory service is working
- Check session ID mapping

## Next Steps After Integration

1. **Optimize Performance**
   - Tune Nova Sonic parameters
   - Optimize context loading
   - Add caching layers

2. **Add Features**
   - Multi-language support
   - Voice emotion detection
   - Session recording (optional)

3. **Scale Testing**
   - Load test with multiple concurrent sessions
   - Optimize ECS auto-scaling
   - Monitor costs

4. **Production Hardening**
   - Add comprehensive error handling
   - Implement retry logic
   - Add detailed logging
   - Set up alerts

## Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents Framework](https://docs.livekit.io/agents/)
- [AWS Bedrock Plugin](https://docs.livekit.io/agents/models/llm/plugins/aws/)
- [AWS Blog: Nova Sonic + LiveKit](https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/)
- [LiveKit Examples GitHub](https://github.com/livekit/agents/tree/main/examples)

---

🏆 **Breaking Barriers UK 2026 Compliant**
- ✅ Uses permitted AWS services (Bedrock, ECS, Lambda, DynamoDB)
- ✅ Deploys to us-west-2 region
- ✅ Open-source LiveKit (no licensing issues)
- ✅ Self-hosted on AWS infrastructure
