w# LiveKit + Nova Sonic 2 Integration Strategy
🏆 Breaking Barriers UK 2026 Hackathon

**Created by**: Tiko Abousteit  
**Date**: 19 January 2026

## Executive Summary

After analyzing the LiveKit infrastructure and Nova Sonic 2 capabilities, we recommend using **LiveKit + Nova Sonic 2** as the optimal architecture for the AI Therapy Platform. This approach is officially supported by AWS and provides significant advantages over custom implementations.

## Architecture Decision

### Selected Approach: LiveKit + Nova Sonic 2

**Why This is Better Than Hybrid (Option 2):**

LiveKit has an **official Nova Sonic 2 plugin** (`livekit-plugins-aws`) that enables speech-to-speech AI in a single model, eliminating the need for separate Transcribe, Claude, and Polly services.

### Architecture Flow

```
Frontend (React + LiveKit SDK)
    ↓ WebRTC Audio
LiveKit Server (ECS)
    ↓ Audio Stream
LiveKit Agent (Python)
    ├─→ Nova Sonic 2 (Bedrock) - Speech-to-Speech AI
    ├─→ Lambda: Load Therapeutic Context (AgentCore)
    ├─→ Lambda: Check Red Flags
    └─→ Lambda: Persist Session Data
```

## What We Keep (Already Built)

✅ **AgentCore Memory Integration**
- `backend/src/services/agentcore_memory_service.py`
- `backend/src/services/conversation_context_service.py`
- `backend/src/services/session_continuity_service.py`
- `backend/src/models/agent_memory.py`

✅ **Therapeutic Prompts**
- `backend/src/services/therapeutic_prompt_service.py`
- `backend/THERAPEUTIC_PROMPTS.md`

✅ **Nova Sonic Configuration**
- `backend/src/config/nova_sonic_config.py`

✅ **All Tests**
- All existing test files remain valid

## What We Remove

❌ **Custom WebSocket Infrastructure**
- `backend/src/lambda_functions/websocket_handlers.py`
- `backend/src/models/websocket_messages.py`
- `backend/src/services/audio_streaming_service.py`

❌ **Separate Services**
- No need for Transcribe (Nova Sonic handles it)
- No need for Claude (Nova Sonic handles it)
- No need for Polly (Nova Sonic handles it)

## What We Add

### 1. LiveKit Infrastructure (ECS)
- LiveKit server container
- Redis for state management
- Load balancers (ALB + NLB)
- Security groups

### 2. LiveKit Agent (Python)
```python
# livekit_agent/agent.py
from livekit.agents import JobContext
from livekit.plugins import aws
import requests

async def entrypoint(ctx: JobContext):
    # Load therapeutic context from existing services
    context = requests.post(
        'https://your-api.com/load-context',
        json={'room_name': ctx.room.name}
    ).json()
    
    # Create Nova Sonic assistant with therapeutic prompts
    assistant = aws.VoiceAssistant(
        model="amazon.nova-sonic-v1:0",
        system_prompt=context['therapeutic_prompt'],
        temperature=0.7
    )
    
    # Monitor for red flags
    @assistant.on("user_speech_committed")
    async def check_red_flags(text: str):
        requests.post(
            'https://your-api.com/check-red-flags',
            json={'session_id': context['session_id'], 'text': text}
        )
    
    # Start the assistant
    assistant.start(ctx.room)
```

### 3. Lambda APIs
- **Token Generator**: Create LiveKit access tokens
- **Context Loader**: Load therapeutic context (uses existing services)
- **Red Flag Handler**: Process red flag events (uses existing services)
- **Session Persistence**: Save session data (uses existing services)

### 4. Frontend Components
- LiveKit React SDK integration
- Replace WebSocket code with LiveKit components

## Benefits Comparison

| Feature | Custom WebSocket | Hybrid (Option 2) | LiveKit + Nova Sonic |
|---------|------------------|-------------------|----------------------|
| Transcription | Custom | Transcribe | Nova Sonic ✅ |
| Conversation | Custom | Claude | Nova Sonic ✅ |
| Synthesis | Custom | Nova Sonic | Nova Sonic ✅ |
| Audio Streaming | Custom code | Custom code | LiveKit ✅ |
| Latency | High | Medium | Low ✅ |
| Services Count | Many | 3 | 1 ✅ |
| Complexity | Very High | High | Low ✅ |
| Time to Build | 40-50 hours | 25-30 hours | 14-19 hours ✅ |
| AWS Official | ❌ | ❌ | ✅ |
| Production Ready | ❌ | Partial | ✅ |

## Implementation Phases

### Phase 1: Deploy LiveKit Infrastructure (2-3 hours)
- Deploy LiveKit server to ECS
- Configure Redis for state management
- Set up security groups and load balancers
- Test connectivity

### Phase 2: Build LiveKit Agent (4-5 hours)
- Create Python agent with Nova Sonic plugin
- Integrate therapeutic prompts (existing service)
- Integrate AgentCore memory (existing service)
- Add red flag monitoring
- Deploy agent to ECS

### Phase 3: Create Lambda APIs (3-4 hours)
- Token generator (new)
- Context loader (uses existing services)
- Red flag handler (uses existing services)
- Session persistence (uses existing services)

### Phase 4: Update Frontend (3-4 hours)
- Install LiveKit React SDK
- Create LiveKitRoom component
- Replace WebSocket code
- Test audio connectivity

### Phase 5: Integration Testing (2-3 hours)
- End-to-end session flow
- Red flag detection validation
- Audio quality verification
- Session persistence testing

**Total Time: 14-19 hours**

## Integration with Existing Services

### Context Loading (Lambda)
```python
def handler(event, context):
    from services.session_continuity_service import SessionContinuityService
    from services.therapeutic_prompt_service import therapeutic_prompt_service
    
    room_name = event['room_name']
    session_id = room_name.replace('session_', '')
    
    # Use existing session continuity service
    continuity = SessionContinuityService()
    context = continuity.resume_conversation(client_id, session_id)
    
    # Use existing therapeutic prompts
    prompt = therapeutic_prompt_service.select_prompt(
        criteria=...,
        client_id=client_id
    )
    
    return {
        'therapeutic_prompt': prompt.prompt_text,
        'context': context,
        'session_id': session_id
    }
```

## Cost Estimation

### LiveKit Infrastructure (Daily)
- ECS Fargate (LiveKit server): ~$3.84/day
- ElastiCache Redis: ~$0.41/day
- Load Balancers: ~$1.50/day
- **Subtotal**: ~$5.75/day

### AWS Services (Daily)
- Lambda invocations: ~$0.20/day
- DynamoDB: ~$0.50/day
- Bedrock (Nova Sonic): ~$2-5/day (usage-based)
- **Subtotal**: ~$3-6/day

**Total Daily Cost**: ~$9-12/day for testing
**Monthly Cost**: ~$270-360/month

### Cost Savings vs Custom
- No Transcribe costs (Nova Sonic handles it)
- No separate TTS costs (Nova Sonic handles it)
- Simpler infrastructure = lower maintenance

## Risk Assessment

### Low Risk Factors
✅ **Official AWS Integration**: Documented in AWS blog
✅ **Open Source**: Full control over LiveKit code
✅ **Self-Hosted**: Deploy on your own AWS infrastructure
✅ **Proven Technology**: Used by thousands of applications
✅ **Existing Work Preserved**: All therapeutic services remain

### Mitigation Strategies
- Start with local Docker testing
- Deploy to dev environment first
- Keep existing code as backup
- Gradual migration (can run both in parallel)

## Success Criteria

✅ Client can join LiveKit room with token
✅ Audio streams to LiveKit agent
✅ Agent loads therapeutic context from AgentCore
✅ Nova Sonic responds with therapeutic prompts
✅ Red flags detected and notifications sent
✅ Session data persists to DynamoDB
✅ Therapist dashboard shows session summaries
✅ End-to-end latency < 300ms

## Official AWS Support

**AWS Blog Post**: [Build real-time conversational AI experiences using Amazon Nova Sonic and LiveKit](https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/)

This is the **recommended pattern** by AWS for building voice AI applications with Nova Sonic 2.

## Recommendation

**STRONGLY RECOMMEND** LiveKit + Nova Sonic 2 because:

1. ✅ **Official AWS Pattern** - Documented and supported by AWS
2. ✅ **Uses All Existing Work** - Therapeutic services integrate perfectly
3. ✅ **Simpler Architecture** - One model instead of three services
4. ✅ **Lower Latency** - Speech-to-speech in single model
5. ✅ **Production-Ready** - LiveKit handles all audio complexity
6. ✅ **Time Savings** - 20-25 hours saved on audio infrastructure
7. ✅ **Lower Cost** - Fewer services = lower cost
8. ✅ **Better Quality** - WebRTC audio > WebSocket audio

## Next Steps

1. ✅ **Review this strategy** - Understand the approach
2. 📖 **Read detailed plan** - `LIVEKIT_INTEGRATION_PLAN.md`
3. 🏗️ **Deploy infrastructure** - Follow Phase 1
4. 🤖 **Build agent** - Follow Phase 2
5. 🔌 **Create APIs** - Follow Phase 3
6. 🎨 **Update frontend** - Follow Phase 4
7. ✅ **Test end-to-end** - Follow Phase 5

## Resources

- **Integration Plan**: `LIVEKIT_INTEGRATION_PLAN.md`
- **Infrastructure Summary**: `LIVEKIT_INFRASTRUCTURE_SUMMARY.md`
- **Migration Guide**: `LIVEKIT_MIGRATION_SUMMARY.md`
- **Quick Reference**: `LIVEKIT_QUICK_REFERENCE.md`
- **AWS Blog**: https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/
- **LiveKit Docs**: https://docs.livekit.io/
- **LiveKit Agents**: https://docs.livekit.io/agents/

---

🏆 **Breaking Barriers UK 2026 Compliant**
- ✅ Uses permitted AWS services (Bedrock, ECS, Lambda, DynamoDB)
- ✅ Deploys to us-west-2 region
- ✅ Open-source LiveKit (no licensing issues)
- ✅ Self-hosted on AWS infrastructure
