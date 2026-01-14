# AgentCore Memory Service Usage Guide

🏆 Breaking Barriers UK 2026 compliant

## Overview

The AgentCore Memory Service provides persistent conversation context and therapeutic profile management for the AI Therapy Platform. It enables therapeutic continuity across sessions by storing and retrieving conversation history, progress notes, and personalized therapeutic approaches.

## Architecture

```
AgentCore Memory Service
├── Models (agent_memory.py)
│   ├── AgentMemory - Main memory container
│   ├── ConversationContext - Session history and progress
│   ├── TherapeuticProfile - Personalized therapeutic settings
│   ├── RetentionPolicy - Memory lifecycle management
│   ├── SessionSummary - Individual session summaries
│   ├── ProgressNote - Therapeutic progress tracking
│   └── PersonalityAdaptation - AI personality adjustments
└── Service (agentcore_memory_service.py)
    ├── Memory CRUD operations
    ├── Context serialization for AI prompts
    └── Memory optimization and cleanup
```

## Key Features

### 1. Memory Creation
Create new memory for a client with customizable retention policies:

```python
from src.services.agentcore_memory_service import AgentCoreMemoryService
from src.models.agent_memory import RetentionPolicyType

service = AgentCoreMemoryService()

# Create memory with standard 90-day retention
memory = service.create_memory(
    client_id="client123",
    language_preference="en",
    retention_policy_type=RetentionPolicyType.STANDARD
)
```

### 2. Memory Retrieval
Retrieve existing memory for session continuity:

```python
# Get complete memory
memory = service.get_memory(client_id="client123")

# Get just conversation context
context = service.get_conversation_context(client_id="client123")

# Get just therapeutic profile
profile = service.get_therapeutic_profile(client_id="client123")
```

### 3. Session Summary Management
Add session summaries after each therapy session:

```python
from src.models.agent_memory import SessionSummary

summary = SessionSummary(
    session_id="session789",
    duration_seconds=1800,
    key_topics=["anxiety", "coping strategies"],
    emotional_state=["calm", "hopeful"],
    therapeutic_progress="Client showed improvement in managing anxiety"
)

updated_memory = service.add_session_summary(
    client_id="client123",
    session_summary=summary
)
```

### 4. Progress Notes
Track therapeutic progress with categorized notes:

```python
from src.models.agent_memory import ProgressNote

note = ProgressNote(
    note_id="note001",
    content="Client demonstrated effective use of breathing techniques",
    category="coping_skills",
    importance=4  # 1-5 scale
)

updated_memory = service.add_progress_note(
    client_id="client123",
    progress_note=note
)
```

### 5. Therapeutic Profile Updates
Customize therapeutic approach based on client needs:

```python
profile_updates = {
    'communication_style': 'direct',
    'preferred_approaches': ['CBT', 'mindfulness'],
    'triggers_to_avoid': ['loud noises', 'crowded spaces'],
    'successful_interventions': ['breathing exercises', 'grounding techniques']
}

updated_memory = service.update_therapeutic_profile(
    client_id="client123",
    profile_updates=profile_updates
)
```

### 6. Personality Adaptations
Track AI personality adjustments for better client engagement:

```python
from src.models.agent_memory import PersonalityAdaptation

adaptation = PersonalityAdaptation(
    adaptation_id="adapt001",
    adaptation_type="communication_pacing",
    description="Adjusted to slower, more deliberate pacing",
    effectiveness_score=0.85
)

updated_memory = service.add_personality_adaptation(
    client_id="client123",
    adaptation=adaptation
)
```

### 7. Context Serialization for AI Prompts
Generate formatted context for AI therapeutic conversations:

```python
# Get formatted context string for AI prompts
context_string = service.serialize_context_for_prompt(client_id="client123")

# Use in therapeutic prompt
therapeutic_prompt = f"""
You are an empathetic AI therapist. Here is the client's context:

{context_string}

Continue the therapeutic conversation with appropriate context awareness.
"""
```

### 8. Memory Cleanup
Delete memory when client requests data deletion (GDPR compliance):

```python
success = service.delete_memory(client_id="client123")
```

## Memory Optimization

The service automatically optimizes memory when it exceeds size limits:

- **Session History**: Keeps most recent 50 sessions
- **Progress Notes**: Removes low-importance notes older than 30 days
- **Personality Adaptations**: Keeps only effective adaptations (score >= 0.6)

## Retention Policies

Three retention policy types are supported:

1. **STANDARD**: 90-day retention with automatic cleanup
2. **EXTENDED**: 180-day retention for long-term therapy
3. **PERMANENT**: No expiration (for special cases)

## Configuration

Memory service configuration is managed in `config/agentcore_config.py`:

```python
# Memory retention
MEMORY_TTL_DAYS = 90  # Standard retention period
MAX_MEMORY_SIZE_KB = 512  # Maximum memory size
MEMORY_OPTIMIZATION_THRESHOLD = 0.8  # Trigger optimization at 80%

# Conversation limits
MAX_CONVERSATION_HISTORY_ITEMS = 50  # Maximum session summaries
MAX_SESSION_SUMMARY_LENGTH = 1000  # Maximum summary length
```

## Integration with Lambda Functions

Example Lambda handler using AgentCore memory:

```python
from src.services.agentcore_memory_service import AgentCoreMemoryService
from src.services.therapeutic_prompt_service import TherapeuticPromptService

def session_start_handler(event, context):
    """Handle therapy session start"""
    client_id = event['clientId']
    
    # Initialize services
    memory_service = AgentCoreMemoryService()
    prompt_service = TherapeuticPromptService()
    
    # Load conversation context
    memory = memory_service.get_memory(client_id)
    
    if memory is None:
        # First session - create new memory
        memory = memory_service.create_memory(client_id)
    
    # Get context for AI prompt
    context_string = memory_service.serialize_context_for_prompt(client_id)
    
    # Generate therapeutic prompt with context
    therapeutic_prompt = prompt_service.generate_session_start_prompt(
        language=memory.therapeutic_profile.language_preference,
        context=context_string
    )
    
    return {
        'statusCode': 200,
        'body': {
            'memoryId': memory.memory_id,
            'therapeuticPrompt': therapeutic_prompt,
            'sessionCount': memory.conversation_context.total_sessions
        }
    }
```

## Error Handling

The service handles common error scenarios:

```python
from botocore.exceptions import ClientError

try:
    memory = service.get_memory(client_id)
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceNotFoundException':
        # Memory doesn't exist - create new one
        memory = service.create_memory(client_id)
    else:
        # Other AWS error
        logger.error(f"AgentCore error: {str(e)}")
        raise
```

## Testing

Run the standalone tests to verify functionality:

```bash
cd backend
python3 tests/test_agentcore_memory_standalone.py
```

## AWS Permissions Required

The Lambda execution role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agent-runtime:GetMemory",
        "bedrock-agent-runtime:PutMemory",
        "bedrock-agent-runtime:DeleteMemory"
      ],
      "Resource": "arn:aws:bedrock-agent-runtime:us-west-2:*:memory/*"
    }
  ]
}
```

## Best Practices

1. **Always load context at session start** - Ensures therapeutic continuity
2. **Update memory after each session** - Keeps context current
3. **Use appropriate retention policies** - Balance storage costs with therapeutic needs
4. **Monitor memory size** - Service auto-optimizes but monitor for issues
5. **Serialize context for prompts** - Use formatted context strings for AI
6. **Handle missing memory gracefully** - Create new memory for first-time clients
7. **Clean up on client deletion** - Respect GDPR data deletion requests

## Performance Considerations

- **Memory retrieval**: ~100-200ms typical latency
- **Memory updates**: ~150-300ms typical latency
- **Context serialization**: <10ms (local operation)
- **Automatic optimization**: Triggered when memory exceeds 80% of size limit

## Monitoring

Key metrics to monitor:

- Memory creation rate
- Memory retrieval latency
- Memory size distribution
- Optimization trigger frequency
- Failed operations count

## Support

For issues or questions:
- Check CloudWatch logs for detailed error messages
- Review AgentCore API documentation
- Contact AWS Breaking Barriers UK 2026 Environment Leads
