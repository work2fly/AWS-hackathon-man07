# Session Continuity Service

## Overview

The Session Continuity Service provides comprehensive cross-session memory persistence, conversation resumption, and therapeutic relationship continuity for the AI Therapy Platform. This service ensures that clients experience seamless therapeutic continuity across multiple sessions.

🏆 Breaking Barriers UK 2026 compliant

**Validates: Requirements 7.1, 7.2**

## Features

### 1. Cross-Session Memory Persistence

- **persist_session_to_memory()**: Persists session data to AgentCore memory
  - Creates session summaries with key topics, emotional states, and milestones
  - Updates total session count and last session date
  - Handles memory creation for new clients
  - Returns persistence status with memory information

- **load_session_context()**: Loads conversation context from previous sessions
  - Retrieves memory from AgentCore
  - Generates optimized context window for AI prompts
  - Includes therapeutic profile, recent sessions, and effective adaptations
  - Returns comprehensive context for session continuity

### 2. Conversation Resumption

- **resume_conversation()**: Resumes conversation with full context loading
  - Generates personalized greetings based on session history
  - Calculates time since last session
  - Provides ongoing topics and therapeutic goals
  - Handles first-time vs. returning clients differently

- **check_session_gap()**: Checks for significant gaps since last session
  - Identifies gaps of 7, 14, or 30+ days
  - Provides recommendations (continue_normally, brief_check_in, check_in_thoroughly, reestablish_rapport)
  - Suggests check-in topics based on gap duration
  - Returns gap information and recommendations

### 3. Therapeutic Relationship Continuity

- **build_therapeutic_relationship()**: Builds and strengthens therapeutic relationship
  - Tracks rapport, trust, and engagement metrics
  - Calculates overall relationship strength
  - Records relationship-building adaptations
  - Provides relationship-building recommendations

- **track_therapeutic_alliance()**: Tracks therapeutic alliance development
  - Monitors alliance metrics (goal agreement, task agreement, bond)
  - Calculates alliance score and trend
  - Creates progress notes for alliance development
  - Provides alliance-specific recommendations

### 4. Memory-Based Personalization

- **personalize_therapeutic_approach()**: Personalizes approach based on memory
  - Analyzes therapeutic profile and effective adaptations
  - Generates personalization recommendations
  - Incorporates session feedback for continuous improvement
  - Calculates personalization level (default, basic, moderate, high)

- **adapt_to_client_preferences()**: Adapts to observed client preferences
  - Updates communication style based on observations
  - Adds preferred and avoided topics
  - Incorporates cultural considerations
  - Records preference adaptations

### 5. Continuity Metrics

- **get_continuity_metrics()**: Provides comprehensive continuity metrics
  - Calculates continuity score (0.0-1.0)
  - Measures session frequency
  - Analyzes topic consistency
  - Assesses relationship strength
  - Returns detailed metrics and insights

## Usage Examples

### Persisting a Session

```python
from services.session_continuity_service import SessionContinuityService

continuity_service = SessionContinuityService()

# After a therapy session
result = continuity_service.persist_session_to_memory(
    client_id="client123",
    session=therapy_session,
    conversation_turns=[
        {"user": "I've been feeling anxious", "ai": "Tell me more about that"},
        {"user": "Work has been stressful", "ai": "What specifically is causing stress?"}
    ],
    emotional_states=["anxious", "hopeful"]
)

print(f"Session persisted: {result['success']}")
print(f"Total sessions: {result['total_sessions']}")
```

### Resuming a Conversation

```python
# At the start of a new session
resumption = continuity_service.resume_conversation(
    client_id="client123",
    new_session_id="session2"
)

print(f"Greeting: {resumption['greeting']}")
print(f"Days since last session: {resumption['days_since_last_session']}")
print(f"Ongoing topics: {resumption['ongoing_topics']}")
```

### Checking Session Gap

```python
# Check if there's a significant gap
gap_check = continuity_service.check_session_gap(
    client_id="client123",
    threshold_days=7
)

if gap_check['has_gap']:
    print(f"Gap detected: {gap_check['days_since_last_session']} days")
    print(f"Recommendation: {gap_check['recommendation']}")
    print(f"Suggested topics: {gap_check['suggested_topics']}")
```

### Building Therapeutic Relationship

```python
# Track relationship metrics
relationship = continuity_service.build_therapeutic_relationship(
    client_id="client123",
    session_id="session2",
    relationship_indicators={
        'rapport_score': 0.8,
        'trust_level': 0.7,
        'engagement_level': 0.9
    }
)

print(f"Relationship strength: {relationship['relationship_strength']}")
print(f"Recommendations: {relationship['recommendations']}")
```

### Personalizing Therapeutic Approach

```python
# Get personalization recommendations
personalization = continuity_service.personalize_therapeutic_approach(
    client_id="client123",
    session_feedback={
        'session_id': 'session1',
        'score': 0.9,
        'notes': 'Very helpful session'
    }
)

print(f"Personalization level: {personalization['personalization_level']}")
print(f"Communication style: {personalization['communication_style']}")
print(f"Recommendations: {personalization['recommendations']}")
```

### Getting Continuity Metrics

```python
# Get comprehensive metrics
metrics = continuity_service.get_continuity_metrics(client_id="client123")

print(f"Continuity score: {metrics['continuity_score']}")
print(f"Total sessions: {metrics['total_sessions']}")
print(f"Session frequency: {metrics['session_frequency']}")
print(f"Topic consistency: {metrics['topic_consistency']}")
print(f"Relationship strength: {metrics['relationship_strength']}")
```

## Integration with Other Services

The Session Continuity Service integrates with:

1. **AgentCore Memory Service**: For persistent memory storage and retrieval
2. **Conversation Context Service**: For conversation tracking and summarization
3. **Session Repository**: For session data management

## Key Benefits

1. **Seamless Continuity**: Clients experience smooth transitions between sessions
2. **Personalized Care**: Therapeutic approach adapts based on client history
3. **Relationship Building**: Tracks and strengthens therapeutic alliance
4. **Memory Optimization**: Manages memory size while preserving important context
5. **Comprehensive Metrics**: Provides insights into therapeutic progress

## Error Handling

All methods include comprehensive error handling:
- Returns success/failure status
- Provides error messages for debugging
- Gracefully handles missing memory
- Creates memory for new clients automatically

## Performance Considerations

- Context windows are optimized for token limits (default 4000 tokens)
- Memory is automatically optimized when size limits are exceeded
- Session history is limited to most recent items
- Progress notes are filtered by importance and recency

## Future Enhancements

- AI-powered session gap analysis
- Predictive relationship strength modeling
- Automated intervention recommendations
- Advanced personalization algorithms
- Multi-modal context integration (audio, text, sentiment)
