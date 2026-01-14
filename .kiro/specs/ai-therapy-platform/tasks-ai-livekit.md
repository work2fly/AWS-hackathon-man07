# AI Team Tasks: AI Therapy Platform (LiveKit-Enhanced)
🏆 Breaking Barriers UK 2026 Hackathon

## Overview

AI team is responsible for LiveKit + Amazon Nova Sonic 2 integration, AWS AgentCore memory management, and therapeutic AI conversation logic. LiveKit eliminates the need for custom audio infrastructure, allowing focus on core therapeutic features.

**Key Change**: Using LiveKit Agents framework with official AWS Nova Sonic plugin instead of custom WebSocket/audio pipeline.

## Team Dependencies

**Requires from Backend Team**:
- LiveKit token generation API (Lambda)
- Agent context loading API (Lambda → AgentCore)
- Red flag notification APIs (Lambda)
- Session persistence APIs (Lambda → DynamoDB)

**Provides to Backend Team**:
- Red flag detection events from agent
- Session conversation data for persistence
- Sentiment analysis results

**Provides to Frontend Team**:
- LiveKit server URL and connection details
- Session state updates via LiveKit events

## Completed Work (Keep)

✅ **Task 1.1**: Nova Sonic 2 configuration - DONE
✅ **Task 1.3**: Therapeutic system prompts - DONE
✅ **Task 2.1**: AgentCore client and memory operations - DONE
✅ **Task 2.2**: Conversation context management - DONE
✅ **Task 2.3**: Session continuity system - DONE

## AI Team Tasks (LiveKit-Enhanced)

- [x] 1. Set up LiveKit infrastructure
  - [x] 1.1 Deploy LiveKit server on AWS ECS
    - Create ECS cluster and task definition
    - Configure LiveKit server with livekit.yaml
    - Set up Application Load Balancer
    - Configure security groups (ports 7880, 7881, 50000-60000)
    - Set up ElastiCache Redis for state management
    - _Requirements: 2.1, 2.2_
    - _Estimated Time: 2-3 hours_

  - [x] 1.2 Configure LiveKit authentication
    - Store API keys in AWS Secrets Manager
    - Configure IAM roles for ECS tasks
    - Set up CloudWatch logging
    - Test server connectivity
    - _Requirements: 1.2, 6.1_
    - _Estimated Time: 1 hour_

- [ ] 2. Implement LiveKit Agent with Nova Sonic
  - [ ] 2.1 Set up agent environment
    - Install livekit-agents and livekit-plugins-aws
    - Configure AWS credentials for Bedrock access
    - Set up Python virtual environment
    - Create agent deployment package
    - _Requirements: 2.3, 3.1_
    - _Estimated Time: 1-2 hours_

  - [ ] 2.2 Build main agent with therapeutic context
    - Create agent.py with Nova Sonic plugin
    - Integrate therapeutic prompts (ALREADY DONE - Task 1.3)
    - Load context from AgentCore (ALREADY DONE - Task 2.3)
    - Implement turn detection and conversation flow
    - Add multi-language support via Nova Sonic
    - _Requirements: 2.3, 2.4, 3.4, 10.1, 10.2, 10.3, 10.4_
    - _Estimated Time: 4-5 hours_

  - [ ] 2.3 Integrate AgentCore memory loading
    - Call Lambda API to load therapeutic context
    - Pass context to Nova Sonic system prompt
    - Handle context loading errors gracefully
    - Cache context for session duration
    - _Requirements: 3.3, 3.6, 3.7, 7.1, 7.2_
    - _Estimated Time: 2 hours_

  - [ ] 2.4 Implement conversation tracking
    - Track user and agent speech turns
    - Store conversation data for persistence
    - Monitor conversation quality metrics
    - Handle interruptions and overlapping speech
    - _Requirements: 7.1, 7.2_
    - _Estimated Time: 2 hours_

- [ ] 3. Implement safety guardrails and red flag detection
  - [ ] 3.1 Create real-time red flag monitoring
    - Monitor user speech for safety triggers
    - Implement pattern recognition for self-harm indicators
    - Add suicidal ideation detection
    - Build abuse and violence mention detection
    - _Requirements: 4.1, 4.2, 4.3_
    - _Estimated Time: 3-4 hours_

  - [ ] 3.2 Integrate red flag notification system
    - Call Lambda API when red flags detected
    - Pass context and severity information
    - Handle notification failures gracefully
    - Log all red flag events
    - _Requirements: 4.4, 4.5, 4.6_
    - _Estimated Time: 2 hours_

  - [ ] 3.3 Implement safety guardrails
    - Filter inappropriate AI responses
    - Enforce therapeutic boundaries
    - Prevent harmful content generation
    - Add response quality validation
    - _Requirements: 3.5_
    - _Estimated Time: 2-3 hours_

  - [ ] 3.4 Write property test for safety features
    - **Property 7: Safety Guardrails and Filtering**
    - **Property 8: Comprehensive Red Flag Detection**
    - **Validates: Requirements 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**
    - _Estimated Time: 2 hours_

- [ ] 4. Build sentiment analysis and progress tracking
  - [ ] 4.1 Create real-time sentiment analysis
    - Analyze conversation sentiment during session
    - Track emotional state changes
    - Identify mood patterns
    - Generate sentiment scores
    - _Requirements: 7.3_
    - _Estimated Time: 3 hours_

  - [ ] 4.2 Build session summarization
    - Extract key topics from conversation
    - Identify therapeutic milestones
    - Generate privacy-compliant summaries (no transcripts)
    - Format summaries for therapist dashboard
    - _Requirements: 7.3, 7.4, 5.2, 5.5_
    - _Estimated Time: 3 hours_

  - [ ] 4.3 Implement progress tracking
    - Track therapeutic progress indicators
    - Identify intervention opportunities
    - Generate progress reports
    - Store progress data in AgentCore
    - _Requirements: 7.3, 7.5_
    - _Estimated Time: 2 hours_

  - [ ] 4.4 Write property test for sentiment analysis
    - **Property 13: Session Sentiment Analysis**
    - **Validates: Requirements 7.3, 7.5**
    - _Estimated Time: 1 hour_

- [ ] 5. Implement session persistence
  - [ ] 5.1 Build session data persistence
    - Call Lambda API to persist conversation data
    - Store session metadata in DynamoDB
    - Update AgentCore memory with session summary
    - Handle persistence failures with retry logic
    - _Requirements: 7.1, 7.2, 7.6_
    - _Estimated Time: 2 hours_

  - [ ] 5.2 Implement session cleanup
    - Clean up LiveKit room after session
    - Archive conversation data
    - Update session status in DynamoDB
    - Trigger post-session workflows
    - _Requirements: 7.6_
    - _Estimated Time: 1 hour_

- [ ] 6. Deploy and test agent
  - [ ] 6.1 Deploy agent to AWS
    - Create ECS task definition for agent
    - Configure auto-scaling for multiple agents
    - Set up health checks and monitoring
    - Deploy to us-west-2 region
    - _Requirements: 8.1, 8.4_
    - _Estimated Time: 2 hours_

  - [ ] 6.2 Integration testing
    - Test agent connection to LiveKit server
    - Verify Nova Sonic integration
    - Test context loading from AgentCore
    - Validate red flag detection
    - Test session persistence
    - _Requirements: 8.1, 8.2, 8.3_
    - _Estimated Time: 3 hours_

  - [ ] 6.3 End-to-end testing
    - Test complete therapy session flow
    - Verify audio quality and latency
    - Test multi-language support
    - Validate safety features
    - Test therapist notifications
    - _Requirements: 8.1, 8.2, 8.3_
    - _Estimated Time: 2 hours_

  - [ ] 6.4 Performance optimization
    - Optimize agent response time
    - Tune Nova Sonic parameters
    - Optimize context loading
    - Monitor resource usage
    - _Requirements: 8.4_
    - _Estimated Time: 2 hours_

## Eliminated Tasks (Thanks to LiveKit)

❌ **Task 1.2**: Design audio streaming protocols - LiveKit handles this
❌ **Task 3.1**: Set up Strands Agent SDK - Using LiveKit Agents instead
❌ **Task 3.2**: Build therapeutic conversation engine - Nova Sonic + LiveKit handles this
❌ **Task 3.3**: Create multi-language support - Nova Sonic has built-in support
❌ **Task 6.1**: Create audio streaming and buffering - LiveKit handles this
❌ **Task 6.2**: Build language detection - Nova Sonic handles this
❌ **Task 6.3**: Create voice synthesis - Nova Sonic handles this
❌ **Task 6.4**: Add error handling for audio - LiveKit handles this
❌ **Task 7.1**: Build session state management - LiveKit handles this
❌ **Task 7.2**: Implement conversation quality assurance - Simplified with LiveKit
❌ **Task 7.3**: Create personalization engine - Handled by AgentCore memory

**Time Saved**: ~20-25 hours of audio infrastructure work

## Coordination Points

**With Backend Team**:
- LiveKit token generation API endpoint
- Agent context loading API endpoint
- Red flag notification API endpoint
- Session persistence API endpoint
- DynamoDB schema for LiveKitRooms table

**With Frontend Team**:
- LiveKit server URL
- Token request flow
- Session status updates
- Error handling patterns

**Integration Milestones**:
- **Day 1 Morning**: LiveKit server deployed and agent running
- **Day 1 Afternoon**: Agent loads context and responds with therapeutic prompts
- **Day 1 Evening**: Red flag detection and notifications working
- **Day 2 Morning**: End-to-end testing with frontend
- **Day 2 Afternoon**: Performance optimization and demo preparation

## Testing Strategy

### Unit Tests
- Agent context loading
- Red flag detection logic
- Sentiment analysis algorithms
- Session data formatting

### Integration Tests
- LiveKit server connectivity
- Nova Sonic API calls
- Lambda API integrations
- AgentCore memory operations

### Property-Based Tests
- **Property 5**: Nova Sonic audio processing (DONE)
- **Property 6**: AgentCore memory integration (TODO)
- **Property 7**: Safety guardrails (TODO)
- **Property 8**: Red flag detection (TODO)
- **Property 13**: Sentiment analysis (TODO)

### End-to-End Tests
- Complete therapy session flow
- Multi-language conversations
- Red flag detection and escalation
- Session persistence and continuity

## Notes

- **Focus on therapeutic features**: LiveKit handles audio infrastructure
- **Leverage existing work**: AgentCore memory and therapeutic prompts are done
- **Prioritize safety**: Red flag detection is critical for user protection
- **Test thoroughly**: End-to-end testing ensures all components work together
- **Monitor performance**: Track latency, resource usage, and costs

## Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents Framework](https://docs.livekit.io/agents/)
- [AWS Bedrock Plugin](https://docs.livekit.io/agents/models/llm/plugins/aws/)
- [AWS Blog: Nova Sonic + LiveKit](https://aws.amazon.com/blogs/machine-learning/build-real-time-conversational-ai-experiences-using-amazon-nova-sonic-and-livekit/)
- [Integration Plan](../../../LIVEKIT_INTEGRATION_PLAN.md)

---

🏆 **Breaking Barriers UK 2026 Compliant**
- ✅ Uses permitted AWS services (Bedrock, ECS, Lambda, DynamoDB)
- ✅ Deploys to us-west-2 region
- ✅ Open-source LiveKit (no licensing issues)
- ✅ Self-hosted on AWS infrastructure
