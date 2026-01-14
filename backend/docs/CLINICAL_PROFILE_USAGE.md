# Clinical Profile System - Usage Guide

🏆 Breaking Barriers UK 2026 compliant

## Overview

The Clinical Profile system provides internal tracking of user therapeutic progress and risk assessment. This data is **NOT visible to users** and is used exclusively by the AI system and clinical staff to provide better support.

## Clinical Profile Fields

### User Information
- `age`: User's age (13-120)
- `gender`: Gender identity
- `note_on_user`: Internal clinical notes (max 2000 chars)
- `medical_conditions`: List of diagnosed conditions or empty list

### Risk Assessment (Auto-updated after each session)
- `domestic_abuse_type`: Type of abuse if applicable
  - `physical`, `emotional_psychological`, `sexual`, `financial_economic`, `digital_technological`, `none`
- `emotional_state`: Current emotional state
  - `fear`, `shame`, `guilt`, `confusion`, `anger`, `sadness`, `hopelessness`, `anxiety`, `numbness`, `low_self_esteem`
- `conversation_preference`: Preferred interaction style
  - `just_listening`, `coping_tools`, `check_in`, `venting`, `self_compassion`
- `self_harm_risk_signal`: Self-harm risk level
  - `none`, `passive`, `concerning`, `acute`, `unknown`
- `user_risk`: Overall risk assessment
  - `low`, `medium`, `high`, `unknown`

### Progress Tracking
- `last_session_timestamp`: Last therapy session datetime
- `total_goals`: Total therapeutic goals set
- `goals_achieved`: Number of goals completed

## Usage Examples

### 1. Create User with Clinical Profile

```python
from backend.src.models.user import (
    User, UserProfile, ClinicalProfile, UserRole,
    DomesticAbuseType, EmotionalState, ConversationPreference,
    SelfHarmRiskSignal, UserRisk
)
from backend.src.data.user_repository import UserRepository

# Create user profile (visible to user)
profile = UserProfile(
    first_name="Jane",
    last_name="Doe",
    timezone="UTC"
)

# Create clinical profile (internal only)
clinical = ClinicalProfile(
    age=28,
    gender="female",
    note_on_user="Initial assessment: experiencing anxiety related to work stress",
    medical_conditions=["generalized anxiety disorder"],
    domestic_abuse_type=DomesticAbuseType.NONE,
    emotional_state=EmotionalState.ANXIETY,
    conversation_preference=ConversationPreference.COPING_TOOLS,
    self_harm_risk_signal=SelfHarmRiskSignal.NONE,
    user_risk=UserRisk.LOW,
    total_goals=3,
    goals_achieved=0
)

# Create user
user = User(
    user_id="user123",
    email="jane@example.com",
    role=UserRole.CLIENT,
    profile=profile,
    clinical_profile=clinical
)

# Save to database
repo = UserRepository()
repo.create_user(user)
```

### 2. Analyze Session and Auto-Update Clinical Profile

```python
from backend.src.services.session_analyzer import SessionAnalyzer

# Session messages
messages = [
    {"role": "user", "content": "I've been feeling really anxious lately"},
    {"role": "assistant", "content": "I hear you. Can you tell me more about what's making you anxious?"},
    {"role": "user", "content": "Work has been overwhelming and I'm scared I'll fail"},
    {"role": "assistant", "content": "Those feelings are valid. Let's explore some coping strategies..."}
]

# Analyze session
analyzer = SessionAnalyzer()
result = analyzer.analyze_session(
    user_id="user123",
    session_id="session456",
    messages=messages
)

# Result includes:
# - updates_applied: {emotional_state, conversation_preference, self_harm_risk, user_risk, last_session_timestamp}
# - red_flags_created: List of red flag IDs if any critical issues detected
# - analysis_summary: Summary of detected patterns
```

### 3. Manual Clinical Profile Update

```python
from backend.src.data.user_repository import UserRepository
from backend.src.models.user import EmotionalState, UserRisk

repo = UserRepository()

# Update specific fields
updates = {
    'emotional_state': EmotionalState.SADNESS,
    'user_risk': UserRisk.MEDIUM,
    'total_goals': 5,
    'goals_achieved': 2
}

success = repo.update_clinical_profile("user123", updates)
```

### 4. Retrieve Clinical Profile (Internal API)

```python
# API call to get clinical profile
GET /api/clinical-profile/{user_id}

# Response:
{
    "user_id": "user123",
    "clinical_profile": {
        "age": 28,
        "gender": "female",
        "note_on_user": "Initial assessment...",
        "medical_conditions": ["generalized anxiety disorder"],
        "domestic_abuse_type": "none",
        "emotional_state": "anxiety",
        "conversation_preference": "coping_tools",
        "self_harm_risk_signal": "none",
        "user_risk": "low",
        "last_session_timestamp": "2026-01-14T10:30:00Z",
        "total_goals": 3,
        "goals_achieved": 0
    }
}
```

### 5. Integration with Red Flag System

When the session analyzer detects concerning patterns, it automatically creates red flags:

```python
# If session contains suicidal ideation
# Analyzer automatically:
# 1. Sets self_harm_risk_signal = ACUTE
# 2. Sets user_risk = HIGH
# 3. Creates RedFlag with type=SUICIDAL_IDEATION, severity=CRITICAL
# 4. Triggers notifications to clinical staff
```

## Automatic Session Analysis Flow

```
User completes session
    ↓
POST /api/analyze-session
    ↓
SessionAnalyzer.analyze_conversation()
    ↓
Detects patterns:
  - Emotional keywords → Update emotional_state
  - Conversation style → Update conversation_preference
  - Risk indicators → Update self_harm_risk_signal, user_risk
  - Crisis keywords → Create red flags
    ↓
UserRepository.update_clinical_profile()
    ↓
RedFlagRepository.create_red_flag() (if needed)
    ↓
Return analysis results
```

## Red Flag Integration

The clinical profile works with the red flag system:

- **ACUTE** self-harm risk → Creates CRITICAL red flag
- **CONCERNING** self-harm risk → Creates HIGH severity red flag
- **Abuse indicators** → Creates HIGH severity abuse red flag
- **Violence indicators** → Creates HIGH severity violence red flag
- **Crisis state** → Creates HIGH severity crisis red flag

## Security Notes

1. **Clinical profiles are INTERNAL ONLY** - never exposed in user-facing APIs
2. **Access control** - only clinical staff and AI system can access
3. **Audit logging** - all updates are logged with timestamps
4. **Encryption** - DynamoDB encryption at rest enabled
5. **Data retention** - follows GDPR compliance requirements

## API Endpoints

### Analyze Session (POST)
```
POST /api/analyze-session
Body: {
    "user_id": "user123",
    "session_id": "session456",
    "messages": [...]
}
```

### Get Clinical Profile (GET - Internal Only)
```
GET /api/clinical-profile/{user_id}
```

### Update Goals (POST)
```
POST /api/update-goals
Body: {
    "user_id": "user123",
    "total_goals": 5,
    "goals_achieved": 2
}
```

## Advanced: Bedrock Integration

For production, replace keyword-based analysis with AWS Bedrock (Claude):

```python
analyzer = SessionAnalyzer()
result = analyzer.analyze_with_bedrock(
    user_id="user123",
    session_id="session456",
    messages=messages
)
```

This provides:
- More accurate emotional state detection
- Better risk assessment
- Contextual understanding
- Multi-language support

**Note**: Stay below 1 RPS for Bedrock to avoid throttling.

## Monitoring

Track clinical profile updates in CloudWatch:
- Session analysis success/failure rates
- Red flag creation frequency
- Risk level distribution
- Goal completion rates

🏆 This system is Breaking Barriers UK 2026 compliant - uses only permitted AWS services (DynamoDB, Lambda, Bedrock).
