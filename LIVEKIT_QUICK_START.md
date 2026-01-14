# LiveKit Quick Start Guide
🏆 Breaking Barriers UK 2026 Hackathon

## TL;DR

LiveKit + Nova Sonic 2 = Production-ready voice AI in hours, not days.

**What it does**: Handles all audio infrastructure (WebRTC, streaming, encoding, turn detection)
**What you build**: Therapeutic AI logic, safety features, session management
**Time saved**: 20-25 hours of audio plumbing

## 5-Minute Overview

### What is LiveKit?

Open-source platform for real-time voice/video applications. Think "Twilio for WebRTC" but self-hosted and free.

### Why LiveKit + Nova Sonic?

AWS officially integrated Nova Sonic with LiveKit. It's the recommended pattern for voice AI on AWS.

**Official AWS Blog**: [Build real-time conversational AI experiences using Amazon Nova Sonic and LiveKit](https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/)

### Architecture in 3 Lines

```
1. React client → LiveKit server (WebRTC audio)
2. LiveKit agent → Nova Sonic (speech-to-speech AI)
3. Agent → Your Lambda APIs (therapeutic logic, red flags, persistence)
```

## What You Need

### AWS Resources
- ✅ ECS cluster (for LiveKit server)
- ✅ Lambda functions (for APIs)
- ✅ DynamoDB (for session data)
- ✅ Bedrock (for Nova Sonic)
- ✅ ElastiCache Redis (for LiveKit state)

### Code Components
- ✅ LiveKit server (Docker image - provided)
- ✅ LiveKit agent (Python - you write this)
- ✅ Backend APIs (Lambda - you write this)
- ✅ Frontend (React + LiveKit SDK - you write this)

## Quick Start Commands

### 1. Test Locally (5 minutes)

```bash
# Start LiveKit server
docker run --rm -p 7880:7880 -p 7881:7881 \
  -e LIVEKIT_KEYS="devkey: secret" \
  livekit/livekit-server

# Install agent dependencies
pip install livekit-agents livekit-plugins-aws

# Run example agent
python examples/nova_sonic_agent.py
```

### 2. Deploy to AWS (2-3 hours)

```bash
# Deploy LiveKit server to ECS
terraform apply -target=module.livekit_server

# Deploy agent to ECS
terraform apply -target=module.livekit_agent

# Deploy Lambda APIs
terraform apply -target=module.livekit_apis
```

### 3. Test End-to-End (30 minutes)

```bash
# Start frontend
cd frontend && npm run dev

# Open browser to http://localhost:3000
# Click "Start Session"
# Speak to AI therapist
# Verify audio works
```

## Code Examples

### Backend: Generate LiveKit Token (Lambda)

```python
from livekit import api

def handler(event, context):
    token = api.AccessToken('api-key', 'api-secret')
    token.with_identity(user_id)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=f"session_{session_id}"
    ))
    return {'token': token.to_jwt()}
```

### Agent: Nova Sonic Integration

```python
from livekit.agents import JobContext
from livekit.plugins import aws

async def entrypoint(ctx: JobContext):
    # Load therapeutic context
    context = await load_context(ctx.room.name)
    
    # Start Nova Sonic assistant
    assistant = aws.VoiceAssistant(
        model="amazon.nova-sonic-v1:0",
        system_prompt=context['therapeutic_prompt']
    )
    assistant.start(ctx.room)
```

### Frontend: React Component

```typescript
import { LiveKitRoom } from '@livekit/components-react';

function TherapySession() {
  const { token, serverUrl } = useLiveKitToken();
  
  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      audio={true}
      video={false}
    >
      <VoiceAssistantUI />
    </LiveKitRoom>
  );
}
```

## What You Keep (Already Done)

✅ AgentCore memory service - KEEP
✅ Therapeutic prompts - KEEP
✅ Session continuity - KEEP
✅ All tests - KEEP

## What You Remove

❌ Custom WebSocket handlers - REMOVE
❌ Audio streaming service - REMOVE
❌ WebSocket message models - REMOVE

## What You Add

🆕 LiveKit server (ECS)
🆕 LiveKit agent (Python)
🆕 Token generator (Lambda)
🆕 Context loader (Lambda)
🆕 Frontend LiveKit components

## Time Estimate

| Phase | Time | What You Do |
|-------|------|-------------|
| Infrastructure | 2-3h | Deploy LiveKit server to ECS |
| Backend APIs | 3-4h | Create Lambda functions |
| Agent | 4-5h | Build Python agent with Nova Sonic |
| Frontend | 3-4h | Integrate LiveKit React SDK |
| Testing | 2-3h | End-to-end validation |
| **Total** | **14-19h** | Full integration |

**Time Saved**: 20-25 hours (vs custom WebSocket implementation)

## Common Questions

### Q: Is LiveKit free?
**A**: Yes, it's open source. You only pay for AWS infrastructure (ECS, Lambda, etc.)

### Q: Can I self-host on AWS?
**A**: Yes, that's the recommended approach for this hackathon.

### Q: Does it work with Nova Sonic?
**A**: Yes, AWS officially integrated it. There's a plugin: `livekit-plugins-aws`

### Q: What about WebSockets?
**A**: LiveKit uses WebRTC, which is better for audio (lower latency, better quality).

### Q: Is it production-ready?
**A**: Yes, used by thousands of applications at scale.

### Q: What if I need help?
**A**: Check the detailed guides:
- `LIVEKIT_INTEGRATION_PLAN.md` - Complete implementation
- `LIVEKIT_MIGRATION_SUMMARY.md` - What changed
- LiveKit docs: https://docs.livekit.io/

## Decision Matrix

| Factor | Custom WebSocket | LiveKit |
|--------|-----------------|---------|
| Development Time | 40-50 hours | 25-30 hours |
| Audio Quality | Good | Excellent |
| Latency | 200-500ms | 100-200ms |
| Features | Build yourself | Built-in |
| Maintenance | You maintain | LiveKit maintains |
| Risk | High (custom code) | Low (proven tech) |
| AWS Support | None | Official blog post |
| **Recommendation** | ❌ | ✅ **Use This** |

## Next Steps

1. **Read**: `LIVEKIT_MIGRATION_SUMMARY.md` (10 min)
2. **Review**: `LIVEKIT_INTEGRATION_PLAN.md` (30 min)
3. **Deploy**: Follow Phase 1 (2-3 hours)
4. **Build**: Follow Phases 2-4 (10-13 hours)
5. **Test**: Follow Phase 5 (2-3 hours)
6. **Demo**: Show off your AI therapist! 🎉

## Resources

- **AWS Blog**: https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/
- **LiveKit Docs**: https://docs.livekit.io/
- **LiveKit Agents**: https://docs.livekit.io/agents/
- **AWS Plugin**: https://docs.livekit.io/agents/models/llm/plugins/aws/
- **Examples**: https://github.com/livekit/agents/tree/main/examples

---

🏆 **Breaking Barriers UK 2026 Compliant**

Ready to build? Start with `LIVEKIT_INTEGRATION_PLAN.md`!
