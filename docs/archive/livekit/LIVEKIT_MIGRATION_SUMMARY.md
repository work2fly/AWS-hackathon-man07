# LiveKit Migration Summary
🏆 Breaking Barriers UK 2026 Hackathon

## Executive Summary

We've updated the AI Therapy Platform architecture to use **LiveKit + Amazon Nova Sonic 2** instead of custom WebSocket audio infrastructure. This change is based on the official AWS integration documented in their [Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/).

**Result**: Eliminates 20-25 hours of audio infrastructure work while providing superior audio quality and production-ready features.

## What Changed

### Architecture

**Before (Custom WebSockets)**:
```
React → API Gateway WebSocket → Lambda → Nova Sonic
  ↓ (manual audio handling)
  ↓ (custom streaming protocol)
  ↓ (connection management)
```

**After (LiveKit)**:
```
React + LiveKit SDK → LiveKit Server → LiveKit Agent → Nova Sonic
  ↓ (WebRTC optimized)
  ↓ (built-in features)
  ↓ (production-ready)
```

### Updated Files

1. **`.kiro/specs/ai-therapy-platform/design.md`**
   - Updated architecture diagrams
   - Added LiveKit components section
   - Removed custom WebSocket sections
   - Added LiveKit + Nova Sonic integration details

2. **`.kiro/specs/ai-therapy-platform/tasks-ai-livekit.md`** (NEW)
   - Revised task list with LiveKit integration
   - Eliminated 11 audio infrastructure tasks
   - Added 6 LiveKit-specific tasks
   - Kept all therapeutic AI tasks

3. **`LIVEKIT_INTEGRATION_PLAN.md`** (NEW)
   - Complete implementation guide
   - Phase-by-phase instructions
   - Code examples for all components
   - Deployment checklist
   - Troubleshooting guide

4. **`LIVEKIT_MIGRATION_SUMMARY.md`** (THIS FILE)
   - Summary of changes
   - Migration guide
   - What to keep vs. what to change

## What We Keep (Already Completed)

✅ **AgentCore Memory Integration** (Tasks 2.1, 2.2, 2.3)
- `backend/src/services/agentcore_memory_service.py` - KEEP
- `backend/src/services/conversation_context_service.py` - KEEP
- `backend/src/services/session_continuity_service.py` - KEEP
- `backend/src/models/agent_memory.py` - KEEP
- All tests for these services - KEEP

✅ **Therapeutic Prompts** (Task 1.3)
- `backend/src/services/therapeutic_prompt_service.py` - KEEP
- `backend/THERAPEUTIC_PROMPTS.md` - KEEP
- All therapeutic prompt tests - KEEP

✅ **Nova Sonic Configuration** (Task 1.1)
- `backend/src/config/nova_sonic_config.py` - KEEP (will be used by LiveKit agent)
- Nova Sonic configuration tests - KEEP

## What We Change/Remove

### Remove (No Longer Needed)

❌ **Custom WebSocket Handlers**
- `backend/src/lambda_functions/websocket_handlers.py` - REMOVE or REPURPOSE
- `backend/src/models/websocket_messages.py` - REMOVE
- `backend/src/services/audio_streaming_service.py` - REMOVE
- `backend/AUDIO_STREAMING_PROTOCOL.md` - ARCHIVE (for reference)

### Add (New LiveKit Components)

🆕 **LiveKit Infrastructure**
- ECS task definition for LiveKit server
- LiveKit server configuration (livekit.yaml)
- Security groups and networking

🆕 **LiveKit Agent**
- `livekit_agent/agent.py` - NEW Python agent
- `livekit_agent/requirements.txt` - NEW dependencies
- Agent deployment configuration

🆕 **Backend APIs for LiveKit**
- `backend/src/lambda_functions/livekit_token_generator.py` - NEW
- `backend/src/lambda_functions/agent_context_loader.py` - NEW
- `backend/src/lambda_functions/red_flag_handler.py` - NEW
- `backend/src/lambda_functions/session_persist_handler.py` - NEW

🆕 **Frontend LiveKit Integration**
- `frontend/src/components/client/LiveKitRoom.tsx` - NEW
- `frontend/src/hooks/useLiveKit.ts` - NEW
- `frontend/src/services/livekit.ts` - NEW

🆕 **DynamoDB Table**
- LiveKitRooms table for room tracking

## Migration Steps

### Step 1: Review Documentation (30 minutes)

Read these files in order:
1. `LIVEKIT_INTEGRATION_PLAN.md` - Complete implementation guide
2. `.kiro/specs/ai-therapy-platform/design.md` - Updated architecture
3. `.kiro/specs/ai-therapy-platform/tasks-ai-livekit.md` - New task list

### Step 2: Deploy LiveKit Infrastructure (2-3 hours)

Follow Phase 1 in `LIVEKIT_INTEGRATION_PLAN.md`:
- Deploy LiveKit server to ECS
- Configure security groups
- Set up Redis for state management
- Test server connectivity

### Step 3: Create Backend APIs (3-4 hours)

Follow Phase 2 in `LIVEKIT_INTEGRATION_PLAN.md`:
- Create Lambda functions for token generation
- Create context loader API (uses existing AgentCore services)
- Create red flag handler API
- Create session persistence API
- Deploy and test APIs

### Step 4: Build LiveKit Agent (4-5 hours)

Follow Phase 3 in `LIVEKIT_INTEGRATION_PLAN.md`:
- Set up Python environment
- Create agent.py with Nova Sonic plugin
- Integrate therapeutic prompts (already done)
- Integrate AgentCore memory (already done)
- Add red flag detection
- Deploy agent to ECS/EC2

### Step 5: Update Frontend (3-4 hours)

Follow Phase 4 in `LIVEKIT_INTEGRATION_PLAN.md`:
- Install LiveKit React SDK
- Create LiveKitRoom component
- Update session flow to use LiveKit
- Test audio connectivity

### Step 6: Integration Testing (2-3 hours)

Follow Phase 5 in `LIVEKIT_INTEGRATION_PLAN.md`:
- Test end-to-end session flow
- Verify red flag detection
- Test session persistence
- Validate audio quality

## Task Comparison

### Original Tasks (Custom WebSockets)
- Total: 8 major tasks, 35 sub-tasks
- Audio infrastructure: 11 sub-tasks
- Therapeutic features: 24 sub-tasks
- **Estimated Time**: 40-50 hours

### New Tasks (LiveKit)
- Total: 6 major tasks, 24 sub-tasks
- LiveKit integration: 6 sub-tasks
- Therapeutic features: 18 sub-tasks (some simplified)
- **Estimated Time**: 25-30 hours

**Time Saved**: 15-20 hours

## Benefits of LiveKit Integration

### Technical Benefits
✅ **Production-Ready**: Battle-tested WebRTC infrastructure
✅ **Official AWS Support**: Documented Nova Sonic integration
✅ **Superior Audio Quality**: WebRTC vs WebSocket streaming
✅ **Built-in Features**: VAD, noise suppression, turn detection
✅ **Auto-Scaling**: Handles load automatically
✅ **Open Source**: Self-host on AWS with full control

### Development Benefits
✅ **Faster Development**: No custom audio code needed
✅ **Focus on Value**: Spend time on therapeutic features
✅ **Fewer Bugs**: Less custom code = fewer bugs
✅ **Better Testing**: Test therapeutic logic, not audio plumbing
✅ **Easier Maintenance**: LiveKit handles infrastructure updates

### Hackathon Benefits
✅ **Time Savings**: 15-20 hours saved
✅ **Better Demo**: Superior audio quality
✅ **More Features**: Time for therapeutic enhancements
✅ **Lower Risk**: Proven technology vs custom implementation

## Cost Comparison

### Custom WebSocket Approach
- API Gateway WebSocket: ~$1/million messages
- Lambda: ~$0.20/million requests
- **Estimated**: $5-8/day for testing

### LiveKit Approach
- ECS Fargate (LiveKit server): ~$3.84/day
- ElastiCache Redis: ~$0.41/day
- Lambda: ~$0.20/million requests
- **Estimated**: $5-10/day for testing

**Cost Difference**: Minimal (~$2/day more for LiveKit)
**Value**: Significantly better audio quality and features

## Risk Assessment

### Low Risk
✅ **Official AWS Integration**: Documented and supported
✅ **Open Source**: Can inspect and modify code
✅ **Self-Hosted**: Full control over infrastructure
✅ **Proven Technology**: Used by thousands of applications

### Mitigation Strategies
- Start with local testing (Docker)
- Deploy to dev environment first
- Keep existing code as backup
- Gradual migration (can run both in parallel)

## Recommendation

**STRONGLY RECOMMEND** adopting LiveKit for the hackathon:

1. **Official AWS Pattern**: This is the recommended approach per AWS blog
2. **Time Savings**: 15-20 hours saved on audio infrastructure
3. **Better Quality**: Superior audio vs custom WebSocket implementation
4. **Lower Risk**: Proven technology vs custom code
5. **Focus on Value**: Spend time on therapeutic features, not plumbing

## Next Steps

1. ✅ **Review this summary** - You're here!
2. 📖 **Read integration plan** - `LIVEKIT_INTEGRATION_PLAN.md`
3. 🏗️ **Start Phase 1** - Deploy LiveKit server
4. 🔌 **Build Phase 2** - Create backend APIs
5. 🤖 **Implement Phase 3** - Build LiveKit agent
6. 🎨 **Update Phase 4** - Frontend integration
7. ✅ **Test Phase 5** - End-to-end validation

## Questions?

Refer to:
- **Implementation Details**: `LIVEKIT_INTEGRATION_PLAN.md`
- **Architecture**: `.kiro/specs/ai-therapy-platform/design.md`
- **Tasks**: `.kiro/specs/ai-therapy-platform/tasks-ai-livekit.md`
- **AWS Blog**: https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/
- **LiveKit Docs**: https://docs.livekit.io/

---

🏆 **Breaking Barriers UK 2026 Compliant**
- ✅ Uses permitted AWS services
- ✅ Deploys to us-west-2 region
- ✅ Open-source technology
- ✅ Self-hosted on AWS
